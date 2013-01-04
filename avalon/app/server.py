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

import avalon.app.factory
import avalon.app.plugins




APP_PATH = '/avalon'



def setup_signal_handler():
    """ """
    def _exit_handler(signum, frame):
        """Handle TERM and INT by exiting."""
        if signum in (signal.SIGTERM, signal.SIGINT):
            raise SystemExit()

    signal.signal(signal.SIGINT, _exit_handler)
    signal.signal(signal.SIGTERM, _exit_handler)


def setup_cherrypy_env():
    """ """
    cherrypy.config.update({'environment': 'production'})
    cherrypy.log.access_file = None
    cherrypy.log.error_file = None
    cherrypy.log.screen = False


def get_required_files(app_config):
    """ """
    return set([
        app_config.access_log,
        app_config.error_log,
        app_config.db_path])


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
        # TODO: Push object creation up into avalonmsd
        setup_signal_handler()
        setup_cherrypy_env()

        self._log = avalon.app.factory.new_logger(self._app_config, cherrypy.log)
        self._db = avalon.app.factory.new_db_engine(self._app_config, self._log)
        self._db.connect()
        self._handler = avalon.app.factory.new_handler(self._db)
        self._server = avalon.app.factory.new_server(
            self._app_config,
            self._log,
            self._handler,
            APP_PATH)

    def start(self):
        """ """
        self._log.info("Starting server...")
        config = avalon.app.plugins.PluginManagerConfig()
        config.bus = cherrypy.process.wspbus.Bus()
        config.server = self._server
        config.log = self._log
        config.db = self._db

        engine = avalon.app.plugins.PluginManager(config)
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

