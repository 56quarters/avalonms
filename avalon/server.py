# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


"""HTTP server for running the request handler application."""

import logging
import traceback

from cherrypy.wsgiserver import CherryPyWSGIServer


__all__ = [
    'AvalonServer',
    'AvalonServerConfig'
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
    logging mechanism and support reloading any in-memory state
    of the application handler.
    """

    def __init__(self, config):
        """Call the parent constructor and set our error logger."""
        super(AvalonServer, self).__init__(
            config.bind_addr,
            config.application,
            numthreads=config.num_threads,
            request_queue_size=config.queue_size)

        self._handler = config.application.root
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
        self._handler.reload()
        self._handler.ready = True
        self._log.info("Handler caches reloaded")

    def start(self):
        """Run the server forever."""
        self._log.info('HTTP server handling requests...')
        super(AvalonServer, self).start()

    def stop(self):
        """Stop the server."""
        self._log.info('Stopping HTTP server...')
        super(AvalonServer, self).stop()

