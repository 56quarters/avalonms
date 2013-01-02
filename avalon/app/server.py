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


import signal

import cherrypy
from cherrypy._cptree import Application as CherryPyApplication

import avalon.server



def setup_signal_handler():
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
        self._handler = avalon.app.new_handler(self._db)
        self._server = new_server(self._app_config, self._log, self._handler)

    def start(self):
        """ """
        pass


