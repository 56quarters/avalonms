# -*- coding: utf-8 -*-
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


import errno
import os
import os.path
import signal
import time
import threading
import traceback

import cherrypy
import daemon

import avalon.exc
import avalon.log
import avalon.models
import avalon.scan
import avalon.services
import avalon.web


APP_PATH = '/avalon'


# TODO: Look into setting up a timedout response monitor


class AvalonMS(object):

    """Wrapper around the main functionality of the Avalon MS, database
    connections, collection scanning, request handling, and 
    daemonization.
    """

    def __init__(self, config):
        """Set the application configuration, create a logger, and
        set up signal handlers.
        """
        default_signal_handler()

        # Configure the global CherryPy environment before we setup
        # our logger so that we make sure to clear any existing logging
        # and use the 'production' environment.
        self._configure_env()

        self._config = config
        self._log = self._get_logger()
        self._db = None

    def _configure_env(self):
        """Configure the global cherrypy environment."""
        cherrypy.config.update({'environment': 'production'})
        cherrypy.log.access_file = None
        cherrypy.log.error_file = None

    def _get_db_url(self):
        """Get a database connection URL from the path to the SQLite database."""
        return 'sqlite:///%s' % self._config.db_path

    def _get_logger(self):
        """Configure and return the application logger."""
        config = avalon.log.AvalonLogConfig()
        config.log_root = cherrypy.log
        config.access_path = self._config.access_log
        config.error_path = self._config.error_log
        return avalon.log.AvalonLog(config)

    def _get_server(self):
        """Configure and return the application server."""
        config = avalon.web.AvalonServerConfig()

        config.log = self._log
        config.bind_addr = (self._config.server_address, self._config.server_port)
        config.num_threads = self._config.server_threads
        config.queue_size = self._config.server_queue
        config.application = cherrypy.tree.mount(
            avalon.web.AvalonHandler(self._db), 
            script_name=APP_PATH)

        return avalon.web.AvalonServer(config)

    def connect(self):
        """Create a database session handler and perform the initial
        database setup for the application.
        """
        self._log.info("Connecting to database...")
        self._db = avalon.models.SessionHandler(self._get_db_url(), self._log)
        # Clean the database (drop and recreate tables) unless
        # the user has requested not to rescan the collection.
        should_clean = not self._config.no_scan

        if should_clean:
            self._log.info("Removing existing collection information...")
        self._db.connect(clean=should_clean)

    def scan(self):
        """Read audio metadata from files in the collection and insert it
        into the database unless the 'no scan' configuration setting is
        true.
        """
        if self._db is None:
            raise avalon.exc.DatabaseError(
                "Can't scan collection: database is not connected")

        if self._config.no_scan:
            self._log.info("Skipping music collection scan...")
            return
        
        self._log.info("Scanning music collection...")
        files = avalon.scan.get_files(os.path.abspath(self._config.collection))
        tags = avalon.scan.get_tags(files)
        loader = avalon.services.InsertService(self._db)
        loader.insert(tags.values())

    def serve(self):
        """Install signal handlers for the server and begin handling requests."""
        if self._db is None:
            raise avalon.exc.DatabaseError(
                "Can't start server: database is not connected")

        self._log.info("Starting server...")
        conf = AvalonEngineConfig()
        conf.bus = cherrypy.process.wspbus.Bus()
        conf.server = self._get_server()
        conf.log = self._log
        conf.db = self._db

        engine = AvalonEngine(conf)
        if self._config.daemon:
            engine.enable_daemon(
                avalon.util.get_uid(self._config.daemon_user),
                avalon.util.get_gid(self._config.daemon_group))

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

    """Manage option and required subscribers to a message bus.

    Allow optional plugins to be registered with the bus and
    register required ones before the bus sends a START message.
    """

    def __init__(self, config):
        """Set the bus, log, db handler, and server."""
        self._bus = config.bus
        self._log = config.log
        self._db = config.db
        self._server = config.server

    def enable_signal_handler(self):
        """Enable and configure the signal handler plugin."""
        h = cherrypy.process.plugins.SignalHandler(self._bus)
        h.handlers = self._get_handlers()
        h.subscribe()

    def enable_server(self):
        """Enable and configure the web server plugin."""
        h = avalon.web.AvalonServerPlugin(
            self._bus, 
            httpserver=self._server,
            bind_addr=self._server.bind_addr)
        h.subscribe()

    def enable_logger(self):
        """Enable the logging plugin."""
        h = avalon.log.AvalonLogPlugin(self._bus, self._log)
        h.subscribe()

    def enable_daemon(self, uid, gid):
        """Enable and configure any plugins needed to run in daemon mode."""
        # Daemon mode entails the actual daemonization process
        # which includes preserving any open file descriptors.
        h = DaemonPlugin(self._bus, self._log.get_open_fds())
        h.subscribe()

        if not avalon.util.are_root():
            return

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

        # Set the logs to be owned by the user we will be switching
        # to since we need write access as the non-super user.
        h = FilePermissionPlugin(
            self._bus,
            self._log.get_open_paths(),
            uid=uid,
            gid=gid)
        h.subscribe()

    def start(self):
        """Register default subscribers and send a START message."""
        self.enable_logger()
        self.enable_signal_handler()
        self.enable_server()

        self._bus.start()
        self._bus.block()

    def stop(self):
        """Send STOP message to all subscribers."""
        self._bus.stop()

    def _get_handlers(self):
        """Get a mapping of signal names to handlers."""
        return {
            'SIGTERM': self._bus.exit,
            'SIGINT': self._bus.exit,
            'SIGUSR1': self._bus.graceful
            }


def default_signal_handler():
    """Simple signal handler to quietly handle ^C."""

    def _exit_handler(signum, frame):
        """Handle TERM and INT by exiting."""
        if signum in (signal.SIGTERM, signal.SIGINT):
            raise SystemExit()
    
    signal.signal(signal.SIGINT, _exit_handler)
    signal.signal(signal.SIGTERM, _exit_handler)
        

class DaemonPlugin(cherrypy.process.plugins.SimplePlugin):

    """Adapt the python-daemon lib to work as a CherryPy plugin."""

    def __init__(self, bus, file_fds):
        """Store the bus and files that are open."""
        super(DaemonPlugin, self).__init__(bus)
        self._context = daemon.DaemonContext()
        self._file_fds = file_fds

    def start(self):
        """Double fork and become a daemon."""
        self._context.files_preserve = self._file_fds
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

    def __init__(self, bus, files, uid=None, gid=None):
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
            if avalon.util.is_perm_error(e):
                raise avalon.exc.PermissionError(
                    'Could not change ownership of file '
                    '[%s]: %s' % (log_file, e))
            # Not an expected permission or access related
            # error rethrow since we can't handle this.
            raise

    def start(self):
        """Fix ownership of each file."""
        for log_file in self._files:
            self._fix(log_file)
    
    # Use a higher priority than the DropPrivileges plugin
    # so that the logs are owned correctly before we lose
    # the ability to change it.
    start.priority = 50



