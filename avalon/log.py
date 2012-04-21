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

    _msg_fmt = '%(levelname)s %(asctime)s %(message)s'

    _date_fmt = '%Y-%m-%d %H:%M:%S'

    def __init__(self, config):
        """ Set the path to the log file or None to use stderr."""
        self._access_path = config.access_path
        self._error_path = config.error_path
        self._level = config.log_level

        self._logger = None
        self._handle = None
        self._setup()

    def get_open_fd(self):
        """ Get the fileno of the open log file."""
        if not self._handle:
            return -1
        return self._handle.fileno()

    def _setup(self):
        """
        """
        log = logging.getLogger('avalon')
        formatter = logging.Formatter(self._msg_fmt, self._date_fmt)

        """
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
        """

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


