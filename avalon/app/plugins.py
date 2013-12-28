# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2013 TSH Labs <projects@tshlabs.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""Plugins that provide the functionality of the music server as subscribers
to a message bus.
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
import avalon.web.controller
import avalon.web.filtering
import avalon.web.search
from avalon.models import Album, Artist, Genre, Track


__all__ = [
    'CollectionScanPlugin',
    'DummyCollectionScanPlugin',
    'DaemonPlugin',
    'FilePermissionPlugin',
    'PluginEngine',
    'PluginEngineConfig ',
    'ServerPlugin',
    'LogPlugin'
]


class PluginEngineConfig(object):
    """Configuration for the message bus wrapper."""

    def __init__(self):
        self.bus = None
        self.log = None
        self.db = None
        self.server = None


class PluginEngine(object):
    """Manage optional and required subscribers to a message bus.

    Allow optional plugins to be registered with the bus and
    register required ones before the bus sends a START message.
    """

    def __init__(self, config):
        """Set the bus, log, db handler, and server."""
        self._bus = config.bus
        self._log = config.log
        self._db = config.db
        self._server = config.server
        self._scanning = False

    def enable_signal_handler(self):
        """Enable and configure the signal handler plugin (enabled by default)."""
        h = cherrypy.process.plugins.SignalHandler(self._bus)
        h.handlers = self._get_handlers()
        h.subscribe()

    def enable_server(self):
        """Enable and configure the web server plugin (enabled by default)."""
        h = ServerPlugin(
            self._bus,
            httpserver=self._server,
            bind_addr=self._server.bind_addr)
        h.subscribe()

    def enable_logger(self):
        """Enable the logging plugin (enabled by default)."""
        h = LogPlugin(self._bus, self._log)
        h.subscribe()

    def enable_daemon(self, uid, gid, required_files):
        """Enable and configure any plugins needed to run in daemon
        mode (not enabled by default)."""
        # Daemon mode entails the actual daemonization process
        # which includes preserving any open file descriptors.
        h = DaemonPlugin(
            self._bus,
            # File handles of files that the application has open
            # right now that need to be preserved as part of the
            # daemonization process. Only the logs should be open
            # at this point.
            files=self._log.get_open_fds())
        h.subscribe()

        if not avalon.util.are_root():
            return

        # Set the logs and database to be owned by the user we will
        # be switching to since we need write access as the non-super
        # user.
        h = FilePermissionPlugin(
            self._bus,
            # Files that may not be open right now but need to be
            # writable by the server once we switch to a different
            # (non-root) user.
            files=required_files,
            uid=uid,
            gid=gid)
        h.subscribe()

        # Switch to a non-super user. This is separate from forking
        # since forking needs to happen before the HTTP server is started
        # (threads and forking don't mix) and dropping privileges needs
        # to happen after we've bound to a port.
        h = cherrypy.process.plugins.DropPrivileges(
            self._bus,
            uid=uid,
            gid=gid,
            umask=0)
        h.subscribe()

    def enable_scan(self, root):
        """Subscribe a listener on the bus to scan (or rescan) the music
        collection (not enabled by default).
        """
        h = CollectionScanPlugin(
            self._bus,
            collection=root,
            db=self._db,
            log=self._log)
        h.subscribe()
        self._scanning = True

    def _enable_dummy_scan(self):
        """Dummy scanner to force a cache reload if the music collection
        isn't already being scanned for real.
        """
        h = DummyCollectionScanPlugin(
            self._bus,
            log=self._log)
        h.subscribe()

    def start(self):
        """Register default subscribers and send a START message."""
        self.enable_logger()
        self.enable_signal_handler()
        self.enable_server()

        if not self._scanning:
            self._enable_dummy_scan()

        self._bus.start()
        self._bus.block()

    def _get_handlers(self):
        """Get a mapping of signal names to handlers."""
        return {
            'SIGTERM': self._bus.exit,
            'SIGINT': self._bus.exit,
            'SIGUSR1': self._bus.graceful
        }


class CollectionScanPlugin(cherrypy.process.plugins.SimplePlugin):
    """Read audio metadata from files in the collection and insert it
    into the database.
    """

    def __init__(self, bus, collection=None, db=None, log=None):
        """Set the message bus, root of the music collection, database
        session handler, and logger.
        """
        super(CollectionScanPlugin, self).__init__(bus)
        self._collection = collection
        self._db = db
        self._log = log

    def graceful(self):
        """Scan the music collection for metadata and insert it into a
        database.
        """
        # TODO: There's way too much going on in this method
        # TODO: Lots of objects getting created here instead of being injected

        self._log.info('Scanning music collection...')

        tag_loader = avalon.tags.read.new_loader()
        tag_crawler = avalon.tags.scan.TagCrawler(tag_loader, self._log)
        tag_files = avalon.tags.scan.get_files(os.path.abspath(self._collection))
        tag_metas = tag_crawler.get_tags(tag_files)

        try:
            cleaner = avalon.tags.insert.Cleaner(self._db)
            for cls in (Album, Artist, Genre, Track):
                cleaner.clean_type(cls)
        except avalon.exc.OperationalError, e:
            self._log.error(
                "There was an error attempting to remove old values "
                "from the database and it may be in an inconsistent "
                "state. Please correct the issue and retry the scan. "
                "The error is: %s", str(e))
            return

        try:
            field_loader = avalon.tags.insert.TrackFieldLoader(self._db, tag_metas)
            field_loader.insert(Album, avalon.ids.get_album_id, 'album')
            field_loader.insert(Artist, avalon.ids.get_artist_id, 'artist')
            field_loader.insert(Genre, avalon.ids.get_genre_id, 'genre')

            dao = avalon.cache.ReadOnlyDao(self._db)
            id_cache = avalon.cache.IdLookupCache(dao)
            track_loader = avalon.tags.insert.TrackLoader(self._db, tag_metas, id_cache)
            track_loader.insert(Track, avalon.ids.get_track_id)
        except avalon.exc.OperationalError, e:
            self._log.error(
                "There was an error attempting to insert new values "
                "into the database and it may be in an inconsistent "
                "state. Please correct the issue and retry the scan. "
                "The error is: %s", str(e))

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
    of the server to reload in-memory data stores.
    """

    def __init__(self, bus, log=None):
        """Set our logger and bus."""
        super(DummyCollectionScanPlugin, self).__init__(bus)
        self._log = log

    def start(self):
        """Trigger a 'graceful' event to force a reload of the in-
        memory data stores.
        ."""
        self._log.info('Forcing cache reload...')
        self.bus.graceful()

    start.priority = 100


class DaemonPlugin(cherrypy.process.plugins.SimplePlugin):
    """Adapt the python-daemon lib to work as a CherryPy plugin."""

    # TODO: python-daemon lib doesn't look like it's getting ported
    # to Python 3 anytime soon. Look into using the default CherryPy
    # daemon plugin to get Python 3 support for free. Might be issues
    # with preserving open files? Some sort of start up order issues?

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
