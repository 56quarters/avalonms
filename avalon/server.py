# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2013 TSH Labs <projects@tshlabs.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
        self._app.reload()
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

