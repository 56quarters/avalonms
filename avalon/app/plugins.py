# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright (c) 2012 TSH Labs <projects@tshlabs.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""
"""

import os

import cherrypy
import daemon

import avalon.cache
import avalon.exc
import avalon.ids
import avalon.log
import avalon.models
import avalon.server
import avalon.tags.insert
import avalon.tags.read
import avalon.tags.scan
import avalon.util
import avalon.web.api
import avalon.web.handler
import avalon.web.filtering
import avalon.web.search
from avalon.models import Album, Artist, Genre, Track


__all__ = [
    'CollectionScanPlugin',
    'DummyCollectionScanPlugin',
    'DaemonPlugin',
    'FilePermissionPlugin',
    'ServerPlugin',
    'LogPlugin'
]


class CollectionScanPlugin(cherrypy.process.plugins.SimplePlugin):

    """Read audio metadata from files in the collection and insert it
    into the database.
    """

    def __init__(self, bus, collection=None, db=None, log=None):
        """Set the root of the music collection and database
        session handler.
        """
        super(CollectionScanPlugin, self).__init__(bus)
        self._collection = collection
        self._db = db
        self._log = log

    def graceful(self):
        """Scan the music collection for metadata and insert it into a
        database.
        """
        self._log.info('Scanning music collection...')
        tag_loader = avalon.tags.read.new_loader()
        tag_crawler = avalon.tags.scan.TagCrawler(tag_loader, self._log)
        tag_files = avalon.tags.scan.get_files(os.path.abspath(self._collection))
        tag_metas = tag_crawler.get_tags(tag_files)

        cleaner = avalon.tags.insert.Cleaner(self._db)
        for cls in (Album, Artist, Genre, Track):
            cleaner.clean_all(cls)

        field_loader = avalon.tags.insert.TrackFieldLoader(self._db, tag_metas)
        field_loader.insert(Album, avalon.ids.get_album_id, 'album')
        field_loader.insert(Artist, avalon.ids.get_artist_id, 'artist')
        field_loader.insert(Genre, avalon.ids.get_genre_id, 'genre')

        id_cache = avalon.cache.IdLookupCache(self._db)
        track_loader = avalon.tags.insert.TrackLoader(self._db, tag_metas, id_cache)
        track_loader.insert(Track, avalon.ids.get_track_id)

    # Set the rescan done as part of a graceful to a higher priority
    # than the server reload done for a graceful so that the new db
    # has been built by the time the in-memory stores are reloaded.
    graceful.priority = 45

    def start(self):
        """Trigger a graceful event at the end of start up to force
        the music collection to be rescanned and in-memory stores reloaded.
        """
        self._log.info('Forcing collection scan and cache reload...')
        self.bus.graceful()

    # Set the scan priority lower than everything else so that start
    # up is done when we trigger a graceful to begin scanning.
    start.priority = 100


class DummyCollectionScanPlugin(cherrypy.process.plugins.SimplePlugin):

    """Fake collection scanning plugin that just forces a graceful
    of the server to reload in memory data stores.
    """

    def __init__(self, bus, log=None):
        """Set our logger and bus."""
        super(DummyCollectionScanPlugin, self).__init__(bus)
        self._log = log

    def start(self):
        """Trigger a 'graceful' event to force a reload of the in
        memory data stores.
        ."""
        self._log.info('Forcing cache reload...')
        self.bus.graceful()

    start.priority = 100


class DaemonPlugin(cherrypy.process.plugins.SimplePlugin):

    """Adapt the python-daemon lib to work as a CherryPy plugin."""

    def __init__(self, bus, files=None):
        """Store the bus and files that are open."""
        super(DaemonPlugin, self).__init__(bus)
        self._context = daemon.DaemonContext()
        self._context.files_preserve = files

    def start(self):
        """Double fork and become a daemon."""
        self._context.open()

    # Set the priority higher than server.start so that we have
    # already forked when threads are created by the HTTP server
    # start up process.
    start.priority = 45

    def stop(self):
        """Prepare the daemon to end."""
        self._context.close()


class FilePermissionPlugin(cherrypy.process.plugins.SimplePlugin):

    """Change the ownership of files so that we retain access
    even after dropping root privileges.
    """

    def __init__(self, bus, files=None, uid=None, gid=None):
        """Set the bus, files to fix, and uid/gid to fix with."""
        super(FilePermissionPlugin, self).__init__(bus)
        self._files = files
        self._uid = uid
        self._gid = gid

    def _fix(self, log_file):
        """Change the file to be owned by our user/group."""
        if not os.path.isfile(log_file):
            return

        try:
            os.chown(log_file, self._uid, self._gid)
        except OSError, e:
            if not avalon.util.is_perm_error(e):
                # Not an expected permission or access related
                # error rethrow since we can't handle this.
                raise
            raise avalon.exc.PermissionError(
                'Insufficient permission to change ownership '
                'of file [%s]' % e.filename, e)

    def start(self):
        """Fix ownership of each file."""
        for log_file in self._files:
            self._fix(log_file)

    # Use a higher priority than the DropPrivileges plugin
    # so that the logs are owned correctly before we lose
    # the ability to change it.
    start.priority = 50

class ServerPlugin(cherrypy.process.servers.ServerAdapter):

    """Adapter between our HTTP server and the CherryPy bus system."""

    def subscribe(self):
        """Register start, stop, and graceful handlers."""
        super(ServerPlugin, self).subscribe()
        self.bus.subscribe('graceful', self.httpserver.reload)

    def unsubscribe(self):
        """Unregister start, stop, and graceful handlers."""
        super(ServerPlugin, self).unsubscribe()
        self.bus.unsubscribe('graceful', self.httpserver.reload)


class LogPlugin(cherrypy.process.plugins.SimplePlugin):

    """Adapter to allow our logger to be used as a CherryPy
    plugin for the bus system.

    Supports the 'graceful' and 'log' channels.
    """

    def __init__(self, bus, log):
        super(LogPlugin, self).__init__(bus)
        self._log = log

    def graceful(self):
        """Configure and reinstall our log handlers (including
        reopening log files.
        """
        self._log.info("Reopening logs...")
        self._log.reload()
        self._log.info("Logs reopened")

    # Set the priority for graceful higher than the default so
    # that we can ensure we have a valid log handle when any
    # other graceful subscribers run.
    graceful.priority = 45

    def log(self, msg, level):
        """Log the message at the desired level."""
        # NOTE: CherryPy argument order is reversed compared
        # to the logging module.
        self._log.log(level, msg)
