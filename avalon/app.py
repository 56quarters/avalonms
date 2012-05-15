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
from avalon.exc import DatabaseError


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
        # Configure the global CherryPy environment before we setup
        # our logger so that we make sure to clear any existing logging
        # and use the 'production' environment.
        self._configure_env()

        self._config = config
        self._log = self._get_logger()
        self._db = None

        install_signal_handler()

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
        """ Configure and return the application server."""
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
        tags = avalon.scan.get_tags(files)
        loader = avalon.services.InsertService(self._db)
        loader.insert(tags.values())

    def serve(self):
        """ Install signal handlers for the server and begin handling requests.
        """
        if self._db is None:
            raise DatabaseError("Can't start server: database is not connected")

        self._log.info("Starting server...")
        server = self._get_server()
        bus = cherrypy.process.wspbus.Bus()

        conf = RequestEngineConfig()
        conf.bus = bus
        conf.server = server
        conf.log = self._log

        engine = RequestEngine(conf)
        engine.start()

        self._log.info("Server stopped")


class RequestEngineConfig(object):

    """ """

    def __init__(self):
        self.bus = None
        self.log = None
        self.server = None


class RequestEngine(object):

    """ """

    def __init__(self, config):
        """ """
        self._bus = config.bus
        self._log = config.log
        self._server = config.server

    def start(self):
        """ """
        h = cherrypy.process.servers.ServerAdapter(self._bus, self._server)
        h.subscribe()

        h = cherrypy.process.plugins.SignalHandler(self._bus)
        h.handlers = self._get_handlers()
        h.subscribe()

        h = avalon.log.AvalonLogPlugin(self._bus, self._log)
        h.subscribe()

        self._bus.start()
        self._bus.block()

    def stop(self):
        """ """
        self._bus.stop()

    def _get_handlers(self):
        """ """
        return {
            'SIGTERM': self._bus.exit,
            'SIGINT': self._bus.exit,
            'SIGUSR1': self._bus.graceful
            }
        

def install_signal_handler():
    """Simple signal handler to quietly handle ^C."""

    def _exit_handler(signum, frame):
        """Handle TERM and INT by exiting."""
        if signum in (signal.SIGTERM, signal.SIGINT):
            raise SystemExit()
    
    signal.signal(signal.SIGINT, _exit_handler)
    signal.signal(signal.SIGTERM, _exit_handler)
        

    


