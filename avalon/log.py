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
Simple logging wrapper.
"""


import logging
import sys


__all__ = [
    'AvalonLog'
    ]


class AvalonLog(object):

    """ Handle setting up log formatters and handlers based
        on configuration settings.
    """

    log_msg_fmt = '%(levelname)s %(asctime)s %(message)s'

    log_date_fmt = '%Y-%m-%d %H:%M:%S'

    log_level = logging.INFO

    def __init__(self, log_path=None):
        """ Set the path to the log file or None to use stderr.
        """
        self._path = log_path
        self._log = None
        self._handle = None

    def get_open_fd(self):
        """ Get the fileno of the open log file.
        """
        if not self._handle:
            return -1
        return self._handle.fileno()

    def start(self):
        """ Make sure logging has not already been set up and create
            and install the appropriate log handlers based on whether
            or not we should be using stderr or a log file.
        """
        self.stop()

        log = logging.getLogger('avalong')
        formatter = logging.Formatter(self.log_msg_fmt, self.log_date_fmt)

        if None is self._path:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(formatter)
            log.addHandler(handler)
        else:
            handler = logging.FileHandler(self._path)
            handler.setFormatter(formatter)
            log.addHandler(handler)

        log.setLevel(self.log_level)

        self._handle = handler.stream
        self._log = log

    def stop(self):
        """ Close and remove any log handlers that have been set up.
        """
        if not self._log or not self._handle:
            return

        # Ensure we get a copy of the log handlers since access
        # to them is controlled via locks for threading purposes.
        for handler in list(self._log.handlers):
            try:
                # It's OK to attempt to close the handler even if it's
                # the stderr handler since the logging StreamHandler
                # doesn't actually close the stream because it might be
                # stderr. This allows us to treat all the handlers the same.
                handler.flush()
                handler.close()
            except IOError:
                pass
            self._log.removeHandler(handler)

        self._log = None
        self._handle = None

    def debug(self, msg, *args):
        """Log at DEBUG level."""
        self._log.debug(msg, *args)

    def info(self, msg, *args):
        """Log at INFO level."""
        self._log.info(msg, *args)

    def warn(self, msg, *args):
        """Log at WARNING level."""
        self._log.warn(msg, *args)

    def error(self, msg, *args):
        """Log at ERROR level."""
        self._log.error(msg, *args)

    def critical(self, msg, *args):
        """Log at CRITICAL level."""
        self._log.critical(msg, *args)

    def log(self, level, msg, *args):
        """ Log at the given level."""
        self._log.log(level, msg, *args)


