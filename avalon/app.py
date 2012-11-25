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


"""Main entry point for collection scanning and HTTP server."""


import os.path
import signal

import cherrypy
# Import the cherrypy Application class directly and use it
# instead of using the global cherrypy.tree Tree instance. We
# then pass this wsgi app directly to the server when it starts.
# All this really buys us is making the code path a little
# simpler and easier to understand (plus avoiding some global
# state).
from cherrypy._cptree import Application as CherryPyApplication
import daemon

import avalon.exc
import avalon.log
import avalon.models
import avalon.scan
import avalon.server
import avalon.services
import avalon.web


__all__ = [
    'APP_PATH',
    'AvalonEngine',
    'AvalonEngineConfig',
    'AvalonMS'
    ]


APP_PATH = '/avalon'


def _install_default_signal_handler():
    """Simple signal handler to quietly handle ^C.

    These handlers are only used until the server finishes starting
    a which point they are replaced by the signal handler plugin for
    the server which uses the message bus to shutdown.
    """

    def _exit_handler(signum, frame):
        """Handle TERM and INT by exiting."""
        if signum in (signal.SIGTERM, signal.SIGINT):
            raise SystemExit()
    
    signal.signal(signal.SIGINT, _exit_handler)
    signal.signal(signal.SIGTERM, _exit_handler)


def _setup_cherrypy_env():
    """Configure the global cherrypy environment."""
    cherrypy.config.update({'environment': 'production'})
    cherrypy.log.access_file = None
    cherrypy.log.error_file = None
    cherrypy.log.screen = False


class AvalonMS(object):

    """Wrapper around the main functionality of the Avalon MS, database
    connections, collection scanning, request handling, and 
    daemonization.
    """

    def __init__(self, config):
        """Set the application configuration, create a logger, and
        set up signal handlers.
        """
        _install_default_signal_handler()
        _setup_cherrypy_env()

        self._config = config
        self._log = self._get_logger()
        self._db = None

    def _get_db_engine(self):
        """Configure and return the database handler."""
        url = 'sqlite:///%s' % self._config.db_path
        config = avalon.models.SessionHandlerConfig()
        config.engine = avalon.models.get_engine(url)
        config.session_factory = avalon.models.get_session_factory()
        config.metadata = avalon.models.get_metadata()
        config.log = self._log

        return avalon.models.SessionHandler(config)

    def _get_logger(self):
        """Configure and return the application logger."""
        config = avalon.log.AvalonLogConfig()
        config.log_root = cherrypy.log
        config.access_path = self._config.access_log
        config.error_path = self._config.error_log
        return avalon.log.AvalonLog(config)

    def _get_handler(self):
        """Configure and return the web request handler."""
        config = avalon.web.AvalonHandlerConfig()
        config.track_store = avalon.services.TrackStore(self._db)
        config.album_store = avalon.services.AlbumStore(self._db)
        config.artist_store = avalon.services.ArtistStore(self._db)
        config.genre_store = avalon.services.GenreStore(self._db)
        config.id_cache = avalon.services.IdLookupCache(self._db)
        handler = avalon.web.AvalonHandler(config)
        return avalon.web.AvalonHandlerWrapper(handler)

    def _get_server(self):
        """Configure and return the application server."""
        config = avalon.server.AvalonServerConfig()
        config.log = self._log
        config.bind_addr = (
            self._config.server_address, 
            self._config.server_port)
        config.num_threads = self._config.server_threads
        config.queue_size = self._config.server_queue
        config.application = CherryPyApplication(
            self._get_handler(),
            script_name=APP_PATH)
        return avalon.server.AvalonServer(config)

    def _get_required_files(self):
        """Get the paths of files that we require write access too."""
        return set([
            self._config.access_log,
            self._config.error_log,
            self._config.db_path])

    def connect(self):
        """Create a database session handler and perform the initial
        database setup for the application.
        """
        self._log.info("Connecting to database...")
        self._db = self._get_db_engine()
        self._db.connect()

    def start(self):
        """Install signal handlers for the server and begin handling
        requests.
        """
        # TODO: Look into setting up a timeout checker (like cherrypy.engine)
        if self._db is None:
            raise avalon.exc.DatabaseError(
                "Can't start server: database is not connected")

        self._log.info("Starting server...")
        config = AvalonEngineConfig()
        config.bus = cherrypy.process.wspbus.Bus()
        config.server = self._get_server()
        config.log = self._log
        config.db = self._db

        engine = AvalonEngine(config)
        if self._config.daemon:
            engine.enable_daemon(
                avalon.util.get_uid(self._config.daemon_user),
                avalon.util.get_gid(self._config.daemon_group),
                self._get_required_files())

        if not self._config.no_scan:
            engine.enable_scan(self._config.collection)

        engine.start()
        self._log.info("Server stopped")


class AvalonEngineConfig(object):

    """Configuration for the message bus wrapper."""

    def __init__(self):
        self.bus = None
        self.log = None
        self.db = None
        self.server = None


class AvalonEngine(object):

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
        """Enable and configure the signal handler plugin."""
        h = cherrypy.process.plugins.SignalHandler(self._bus)
        h.handlers = self._get_handlers()
        h.subscribe()

    def enable_server(self):
        """Enable and configure the web server plugin."""
        h = avalon.server.AvalonServerPlugin(
            self._bus, 
            httpserver=self._server,
            bind_addr=self._server.bind_addr)
        h.subscribe()

    def enable_logger(self):
        """Enable the logging plugin."""
        h = avalon.log.AvalonLogPlugin(self._bus, self._log)
        h.subscribe()

    def enable_daemon(self, uid, gid, required_files):
        """Enable and configure any plugins needed to run in daemon mode."""
        # Daemon mode entails the actual daemonization process
        # which includes preserving any open file descriptors.
        h = _DaemonPlugin(
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
        h = _FilePermissionPlugin(
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
        collection.
        """
        h = _CollectionScanPlugin(
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
        h = _DummyCollectionScanPlugin(
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


class _CollectionScanPlugin(cherrypy.process.plugins.SimplePlugin):

    """Read audio metadata from files in the collection and insert it
    into the database.
    """

    def __init__(self, bus, collection=None, db=None, log=None):
        """Set the root of the music collection and database 
        session handler.
        """
        super(_CollectionScanPlugin, self).__init__(bus)
        self._collection = collection
        self._db = db
        self._log = log

    def graceful(self):
        """Scan the music collection for metadata and insert it into a
        database.
        """
        self._log.info('Scanning music collection...')
        files = avalon.scan.get_files(os.path.abspath(self._collection))
        tags = avalon.scan.get_tags(files)
        loader = avalon.services.InsertService(self._db)
        loader.insert(tags)

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


class _DummyCollectionScanPlugin(cherrypy.process.plugins.SimplePlugin):

    """Fake collection scanning plugin that just forces a graceful
    of the server to reload in memory data stores.
    """

    def __init__(self, bus, log=None):
        """Set our logger and bus."""
        super(_DummyCollectionScanPlugin, self).__init__(bus)
        self._log = log

    def start(self):
        """Trigger a 'graceful' event to force a reload of the in
        memory data stores.
        ."""
        self._log.info('Forcing cache reload...')
        self.bus.graceful()

    start.priority = 100


class _DaemonPlugin(cherrypy.process.plugins.SimplePlugin):

    """Adapt the python-daemon lib to work as a CherryPy plugin."""

    def __init__(self, bus, files=None):
        """Store the bus and files that are open."""
        super(_DaemonPlugin, self).__init__(bus)
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


class _FilePermissionPlugin(cherrypy.process.plugins.SimplePlugin):

    """Change the ownership of files so that we retain access
    even after dropping root privileges.
    """

    def __init__(self, bus, files=None, uid=None, gid=None):
        """Set the bus, files to fix, and uid/gid to fix with."""
        super(_FilePermissionPlugin, self).__init__(bus)
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

