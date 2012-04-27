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


import signal

import avalon.log
import avalon.scan
import avalon.services
import avalon.web
from avalon.exc import CollectionError, NetworkError


class AvalonMS(object):

    def __init__(self, opts):
        """
        """
        self._opts = opts
        self._log = self._get_logger()
        self._app = None
        self._db = None

    def _get_app(self):
        """
        """
        root = avalon.web.AvalonHander(self._session_handler)
        return cherrypy.tree.mount(root, script_name='/avalon')

    def _get_logger(self):
        """
        """
        config = avalon.log.AvalonLogConfig()
        config.access_path = self._opts.access_log
        config.error_path = self._opts.error_log
        return avalon.log.AvalonLog(config)

    def connect(self, rescan):
        """
        """
        

    def scan(self, root):
        """
        """
        files = avalon.scan.get_files(os.path.abspath(root))
        if not files:
            raise CollectionError("No files found in collection root %s" % root)
        return avalon.scan.get_tags(files)

    def insert(self, tracks):
        """
        """
        loader = avalon.services.InsertService(
            tracks.values(),
            self._session_factory)
        loader.insert()

    def serve(self, server):
        """
        """
        try:
            server.start()
        except socket.error, e:
            raise NetworkError(e.message, e)

    def get_db(self, opts, log):
        """
        """
        url = 'sqlite:///%s' % opts.db_path
        return avalon.models.SessionHander(url)

    def get_server(self):
        """
        """
        config = avalon.web.AvalonServerConfig()
        config.gateway = self._get_app()
        config.log = self._log
        config.bind_addr = (opts.server_address, opts.server_port)
        config.num_threads = opts.server_threads
        config.queue_size = opts.server_queue
        return avalon.web.AvalonServer(config)


class SignalHandler(object):

    """
    """
    
    def __init__(self):
        """
        """
        self.server = None
        self._install()

    def handle(self, signum, frame):
        """
        """
        if self.server is None:
            self._exit_handler(signum, frame)
        else:
            self._server_handler(signum, frame)

    def _install(self):
        """
        """
        signal.signal(signal.SIGINT, self.handle)
        signal.signal(signal.SIGTERM, self.handle)
        signal.signal(signal.SIGUSR1, self.handle)
        
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

    


