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


import os
import os.path
import signal
import traceback

import cherrypy
import daemon

import avalon.log
import avalon.models
import avalon.scan
import avalon.services
import avalon.web
from avalon.exc import (
    CollectionError,
    DatabaseError)


__all__ = [
    'APP_PATH',
    'AvalonMS',
    'SignalHandler'
    ]


APP_PATH = '/avalon'


class AvalonMS(object):

    """ Wrapper around the main functionality of the Avalon MS, database
        connections, collection scanning, request handling, and 
        daemonization.
    """

    def __init__(self, config):
        """Set the application configuration, create a logger, and
           set up signal handlers.
        """
        self._config = config
        self._log = self._get_logger()
        self._signals = SignalHandler()
        self._db = None

    def _get_db_url(self):
        """Get a database connection URL from the path to the SQLite database."""
        return 'sqlite:///%s' % self._config.db_path

    def _get_logger(self):
        """Configure and return the application logger."""
        config = avalon.log.AvalonLogConfig()
        config.access_path = self._config.access_log
        config.error_path = self._config.error_log
        return avalon.log.AvalonLog(config)

    def _get_server(self):
        """ Configure and return the application server."""
        config = avalon.web.AvalonServerConfig()

        config.log = self._log
        config.bind_addr = (self._config.server_address, self._config.server_port)
        config.num_threads = self._config.server_threads
        config.queue_size = self._config.server_queue
        config.gateway = cherrypy.tree.mount(
            avalon.web.AvalonHandler(self._db), 
            script_name=APP_PATH)

        return avalon.web.AvalonServer(config)

    def connect(self):
        """ Create a database session handler and perform the initial
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
        """ Read audio metadata from files in the collection and insert it
            into the database unless the 'no scan' configuration setting is
            true.
        """
        if self._db is None:
            raise DatabaseError("Can't scan collection: database is not connected")

        if self._config.no_scan:
            self._log.info("Skipping music collection scan...")
            return
        
        self._log.info("Scanning music collection...")
        files = avalon.scan.get_files(os.path.abspath(self._config.collection))
        if not files:
            raise CollectionError(
                "No files found in collection root %s" % self._config.collection)

        tags = avalon.scan.get_tags(files)
        loader = avalon.services.InsertService(tags.values(), self._db)
        loader.insert()

    def serve(self):
        """ Install signal handlers for the server and begin handling requests.
        """
        if self._db is None:
            raise DatabaseError("Can't start server: database is not connected")

        self._log.info("Starting server...")
        server = self._get_server()
        # Give the signal handler a reference to the server
        # so that we can stop the server properly when we get
        # a SIGTERM or any other signal we care to handle.
        self._signals.server = server            

        if self._config.daemon:
            self._start_daemon(server)
        else:
            self._start_foreground(server)
        self._log.info("Server stopped")

    def _start_foreground(self, server):
        """Start the server in the foreground (non-daemon)."""
        server.start()

    def _start_daemon(self, server):
        """ Start the server as a daemon, switching to a different user
            if required.
        """
        context = daemon.DaemonContext()
        context.files_preserve = self._log.get_open_fds()

        with context:
            # Just reinstall our own signal handlers here instead of
            # specifying them when creating the daemon context so that
            # we can keep all the signal logic in the signal handler
            self._signals.install()

            try:
                server.start()
            except Exception, e:
                self._log.critical(
                    '%s: %s', e.message, traceback.format_exc())


class SignalHandler(object):

    """ Respond to signals to allow the server to gracefully shutdown
        or reload log files.
    """
    
    def __init__(self):
        """Install default signals handlers (before server is started)."""
        self.server = None
        self.install()

    def dispatch(self, signum, frame):
        """Route the signal to a handler based if the server has been started."""
        if self.server is None:
            self._exit_handler(signum, frame)
        else:
            self._server_handler(signum, frame)

    def install(self):
        """Install our signal handler."""
        signal.signal(signal.SIGINT, self.dispatch)
        signal.signal(signal.SIGTERM, self.dispatch)
        signal.signal(signal.SIGUSR1, self.dispatch)
        
    def _exit_handler(self, signum, frame):
        """Handle TERM and INT by exiting."""
        if signum in (signal.SIGTERM, signal.SIGINT):
            raise SystemExit()

    def _server_handler(self, signum, frame):
        """ Handle TERM and INT by stopping the server, USR1 by reloading
            log files.
        """
        if signum in (signal.SIGTERM, signal.SIGINT):
            self.server.stop()
        elif signum == signal.SIGUSR1:
            self.server.reload()

    


