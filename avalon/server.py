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


"""HTTP server for running the request handler application."""


import logging

import cherrypy
from cherrypy.wsgiserver import CherryPyWSGIServer


__all__ = [
    'AvalonServer',
    'AvalonServerConfig',
    'AvalonServerPlugin'
    ]


class AvalonServerConfig(object):

    """Configuration for our HTTP server."""

    def __init__(self):
        self.log = None
        self.bind_addr = None
        self.application = None
        self.num_threads = None
        self.queue_size = None


class AvalonServer(CherryPyWSGIServer):

    """Wrap the standard CherryPy server to use our own error
    logging mechanism.
    """

    def __init__(self, config):
        """Call the parent constructor and set our error logger."""
        super(AvalonServer, self).__init__(
            config.bind_addr,
            config.application,
            numthreads=config.num_threads,
            request_queue_size=config.queue_size)
        
        self._app = config.application.root
        self._log = config.log
        self.socket = None

        self._log.info('Server using address %s', config.bind_addr)
        self._log.info('Server using %s threads', config.num_threads)
        self._log.info('Server using %s queued connections', config.queue_size)

    def error_log(self, msg='', level=logging.INFO, trackback=False):
        """Write an error to the log, optionally with a traceback."""
        if trackback:
            msg = '%s: %s' % (msg, traceback.format_exc())
        self._log.log(level, msg)

    def reload(self):
        """Refresh application in-memory caches."""
        try:
            self._app.reload()
        except Exception, e:
            # Something bad happened. Don't kill the app but mark
            # it as down and log the error along with a traceback.
            self._app.ready = False
            self._log.critical(e.message, exc_info=True)
        else:
            self._app.ready = True
            self._log.info("Handler caches reloaded")

    def start(self):
        """Run the server forever."""
        self._log.info('HTTP server handling requests...')
        super(AvalonServer, self).start()
        
    def stop(self):
        """Stop the server."""
        self._log.info('Stopping HTTP server...')
        super(AvalonServer, self).stop()


class AvalonServerPlugin(cherrypy.process.servers.ServerAdapter):

    """Adapter between our HTTP server and the CherryPy bus system."""

    def subscribe(self):
        """Register start, stop, and graceful handlers."""
        super(AvalonServerPlugin, self).subscribe()
        self.bus.subscribe('graceful', self.httpserver.reload)

    def unsubscribe(self):
        """Unregister start, stop, and graceful handlers."""
        super(AvalonServerPlugin, self).unsubscribe()
        self.bus.unsubscribe('graceful', self.httpserver.reload)

