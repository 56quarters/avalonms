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

import cherrypy

import avalon.log
import avalon.models
import avalon.scan
import avalon.services
import avalon.web
from avalon.exc import CollectionError, NetworkError


__all__ = [
    'APP_PATH',
    'AvalonMS'
    ]


APP_PATH='/avalon'


class Factories(object):
    
    def __init__(self):
        self.logger = avalon.log.AvalonLog
        self.app = avalon.web.AvalonHandler
        self.server = avalon.web.AvalonServer
        self.db = avalon.models.SessionHandler


class AvalonMSConfig(object):

    def __init__(self):
        pass


class AvalonMS(object):

    def __init__(self, opts):
        """
        """
        self._opts = opts
        self._log = self._get_logger()
        self._app = None
        self._db = None
        self._signal = SignalHandler()

    def _get_app(self):
        """
        """
        root = avalon.web.AvalonHandler(self._db)
        return cherrypy.tree.mount(root, script_name=APP_PATH)

    def _get_logger(self):
        """
        """
        config = avalon.log.AvalonLogConfig()
        config.access_path = self._opts.access_log
        config.error_path = self._opts.error_log
        return avalon.log.AvalonLog(config)

    def _get_db_url(self):
        """
        """
        return 'sqlite:///%s' % self._opts.db_path

    def _get_server(self):
        """
        """
        config = avalon.web.AvalonServerConfig()
        config.gateway = self._get_app()
        config.log = self._log
        config.bind_addr = (self._opts.server_address, self._opts.server_port)
        config.num_threads = self._opts.server_threads
        config.queue_size = self._opts.server_queue
        return avalon.web.AvalonServer(config)

    def connect(self):
        """
        """
        self._db = avalon.models.SessionHandler(self._get_db_url(), self._log)
        # Clean the database (drop and recreate tables) unless
        # the user has requested not to rescan the collection.
        self._db.connect(clean=not self._opts.no_scan)

    def scan(self):
        """
        """
        files = avalon.scan.get_files(os.path.abspath(self._opts.collection))
        if not files:
            raise CollectionError("No files found in collection root %s" % root)

        tags = avalon.scan.get_tags(files)
        loader = avalon.services.InsertService(tags.values(), self._db)
        loader.insert()

    def serve(self):
        """
        """
        server = self._get_server()
        self._signal.server = server

        try:
            server.start()
        except socket.error, e:
            raise NetworkError(e.message, e)


class SignalHandler(object):

    """
    """
    
    def __init__(self):
        """
        """
        self.server = None
        self.install()

    def dispatch(self, signum, frame):
        """
        """
        if self.server is None:
            self._exit_handler(signum, frame)
        else:
            self._server_handler(signum, frame)

    def install(self):
        """
        """
        signal.signal(signal.SIGINT, self.dispatch)
        signal.signal(signal.SIGTERM, self.dispatch)
        signal.signal(signal.SIGUSR1, self.dispatch)
        
    def _exit_handler(self, signum, frame):
        """
        """
        if signum in (signal.SIGTERM, signal.SIGINT):
            raise SystemExit()

    def _server_handler(self, signum, frame):
        """
        """
        if signum in (signal.SIGTERM, signal.SIGINT):
            self.server.stop()
        elif signum == signal.SIGUSR1:
            self.server.reload()

    


