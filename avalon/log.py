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

import cherrypy


__all__ = [
    'AvalonLogConfig',
    'AvalonLog'
    ]


class AvalonLogConfig(object):

    """Configuration for the logger."""

    def __init__(self):
        self.access_path = None
        self.error_path = None
        self.log_level = logging.INFO


class AvalonLog(object):

    """ Handle setting up log formatters and handlers based
        on configuration settings.
    """

    _access_fmt = '%(message)s'
    
    _error_fmt = '%(levelname)s %(asctime)s %(message)s'

    _date_fmt = '%Y-%m-%d %H:%M:%S'

    def __init__(self, config):
        """ Set the path to the log file or None to use stderr."""
        self._access_path = config.access_path
        self._error_path = config.error_path
        self._level = config.log_level

        self._logger = None
        self._handlers = []
        self.reload()

    def get_open_fds(self):
        """ Get the file number of any open log files."""
        return [
            handler.stream.fileno() for handler in self._handlers if handler.stream]

    def reload(self):
        """ Configure cherrypy logging and install our own handlers."""
        log = cherrypy.log
        log.screen = False
        log.access_file = None
        log.error_file = None

        # Clear any existing handlers we've installed
        for handler in self._handlers:
            log.access_log.removeHandler(handler)
        for handler in self._handlers:
            log.error_log.removeHandler(handler)
        
        self._handlers = []
        self._setup_access_log(log)
        self._setup_error_log(log)

        # Application logging uses the error log
        self._logger = log.error_log

    def _setup_access_log(self, log):
        """
        """
        if self._access_path is None:
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = logging.FileHandler(self._access_path)
        handler.setFormatter(logging.Formatter(self._access_fmt))

        log.access_log.addHandler(handler)
        self._handlers.append(handler)

    def _setup_error_log(self, log):
        """
        """
        if self._error_path is None:
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = logging.FileHandler(self._error_path)
        handler.setFormatter(logging.Formatter(self._error_fmt, self._date_fmt))

        log.error_log.addHandler(handler)
        self._handlers.append(handler)

    def debug(self, msg, *args):
        """Log at DEBUG level."""
        self._logger.debug(msg, *args)

    def info(self, msg, *args):
        """Log at INFO level."""
        self._logger.info(msg, *args)

    def warn(self, msg, *args):
        """Log at WARNING level."""
        self._logger.warn(msg, *args)

    def error(self, msg, *args):
        """Log at ERROR level."""
        self._logger.error(msg, *args)

    def critical(self, msg, *args):
        """Log at CRITICAL level."""
        self._logger.critical(msg, *args)

    def log(self, level, msg, *args):
        """ Log at the given level."""
        self._logger.log(level, msg, *args)


