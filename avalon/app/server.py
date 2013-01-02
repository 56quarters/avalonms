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


import os
import signal

import cherrypy
from cherrypy._cptree import Application as CherryPyApplication

import avalon.app
import avalon.app.plugins
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


def setup_signal_handler():
    """ """
    def _exit_handler(signum, frame):
        """Handle TERM and INT by exiting."""
        if signum in (signal.SIGTERM, signal.SIGINT):
            raise SystemExit()

    signal.signal(signal.SIGINT, _exit_handler)
    signal.signal(signal.SIGTERM, _exit_handler)


def get_required_files(app_config):
    """ """
    return set([
        app_config.access_log,
        app_config.error_log,
        app_config.db_path])


def new_server(app_config, logger, handler):
    """ """
    server_config = avalon.server.AvalonServerConfig()
    server_config.log = logger
    server_config.bind_addr = (
        app_config.server_address,
        app_config.server_port)
    server_config.num_threads = app_config.server_threads
    server_config.queue_size = app_config.server_queue
    server_config.application = CherryPyApplication(
        handler,
        script_name=avalon.app.APP_PATH)
    return avalon.server.AvalonServer(server_config)


class PluginManagerConfig(object):

    """Configuration for the message bus wrapper."""

    def __init__(self):
        self.bus = None
        self.log = None
        self.db = None
        self.server = None


class PluginManager(object):

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
        h = avalon.app.plugins.ServerPlugin(
            self._bus,
            httpserver=self._server,
            bind_addr=self._server.bind_addr)
        h.subscribe()

    def enable_logger(self):
        """Enable the logging plugin (enabled by default)."""
        h = avalon.app.plugins.LogPlugin(self._bus, self._log)
        h.subscribe()

    def enable_daemon(self, uid, gid, required_files):
        """Enable and configure any plugins needed to run in daemon
        mode (not enabled by default)."""
        # Daemon mode entails the actual daemonization process
        # which includes preserving any open file descriptors.
        h = avalon.app.plugins.DaemonPlugin(
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
        h = avalon.app.plugins.FilePermissionPlugin(
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
        h = avalon.app.plugins.CollectionScanPlugin(
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
        h = avalon.app.plugins.DummyCollectionScanPlugin(
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


class AvalonServerApp(object):

    """ """

    def __init__(self, app_config):
        """ """
        self._app_config = app_config
        self._log = None
        self._db = None
        self._handler = None
        self._server = None

    def initialize(self):
        """ """
        setup_signal_handler()
        avalon.app.setup_cherrypy_env()
        self._log = avalon.app.new_logger(self._app_config, cherrypy.log)
        self._db = avalon.app.new_db_engine(self._app_config, self._log)
        self._db.connect()
        self._handler = avalon.app.new_handler(self._db)
        self._server = new_server(self._app_config, self._log, self._handler)

    def start(self):
        """ """
        self._log.info("Starting server...")
        config = PluginManagerConfig()
        config.bus = cherrypy.process.wspbus.Bus()
        config.server = self._server
        config.log = self._log
        config.db = self._db

        engine = PluginManager(config)
        if self._app_config.daemon:
            engine.enable_daemon(
                avalon.util.get_uid(self._app_config.daemon_user),
                avalon.util.get_gid(self._app_config.daemon_group),
                get_required_files())

        if not self._app_config.no_scan:
            engine.enable_scan(self._app_config.collection)

        engine.start()
        self._log.info("Server stopped")
        return engine

