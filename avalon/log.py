# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2013 TSH Labs <projects@tshlabs.org>
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


"""Simple logging wrapper."""


import logging
import sys

import avalon.exc


__all__ = [
    'DEFAULT_LOG_LEVEL',
    'DEFAULT_ACCESS_FMT',
    'DEFAULT_ERROR_FMT',
    'DEFAULT_DATE_FMT',
    'AvalonLog',
    'AvalonLogConfig'
    ]


DEFAULT_LOG_LEVEL = logging.INFO

DEFAULT_ACCESS_FMT = '%(message)s'

DEFAULT_ERROR_FMT = '%(levelname)s %(asctime)s %(message)s'

DEFAULT_DATE_FMT = '%Y-%m-%d %H:%M:%S'


class AvalonLogConfig(object):

    """Configuration for the logger."""

    def __init__(self):
        self.log_root = None
        self.access_path = None
        self.error_path = None
        self.log_level = DEFAULT_LOG_LEVEL
        self.access_fmt = DEFAULT_ACCESS_FMT
        self.error_fmt = DEFAULT_ERROR_FMT
        self.date_fmt = DEFAULT_DATE_FMT


class AvalonLog(object):

    """Handle setting up log formatters and handlers based
    on configuration settings.
    """

    def __init__(self, config):
        """Set the path to the log file or None to use stderr."""
        self._log_root = config.log_root
        self._access_path = config.access_path
        self._error_path = config.error_path
        self._level = config.log_level
        self._access_fmt = config.access_fmt
        self._error_fmt = config.error_fmt
        self._date_fmt = config.date_fmt

        self._logger = None
        self._handlers = []

        self.reload()
        
    def get_open_fds(self):
        """Get the file number of any open log files."""
        return [
            handler.stream.fileno() for handler in self._handlers if handler.stream]

    def reload(self):
        """ Configure logging and install our own handlers."""
        # Clear any existing handlers we've installed
        for handler in self._handlers:
            self._log_root.access_log.removeHandler(handler)
        for handler in self._handlers:
            self._log_root.error_log.removeHandler(handler)
        
        self._handlers = []

        try:
            self._setup_access_log()
            self._setup_error_log()
        except IOError, e:
            if not avalon.util.is_perm_error(e):
                # If this isn't a permission related error 
                # simply reraise the exception untouched.
                raise
            raise avalon.exc.PermissionError(
                'Insufficient permission to create or open '
                'log [%s]' %  e.filename, e)

        # Application logging uses the error log
        self._logger = self._log_root.error_log

    def _setup_access_log(self):
        """Add a configured handler to the access log of the logging root."""
        if self._access_path is None:
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = logging.FileHandler(self._access_path)
        handler.setFormatter(logging.Formatter(self._access_fmt))

        self._log_root.access_log.addHandler(handler)
        self._handlers.append(handler)

    def _setup_error_log(self):
        """Add a configured handler to the error log of the logging root."""
        if self._error_path is None:
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = logging.FileHandler(self._error_path)
        handler.setFormatter(logging.Formatter(self._error_fmt, self._date_fmt))

        self._log_root.error_log.addHandler(handler)
        self._handlers.append(handler)

    def debug(self, msg, *args, **kwargs):
        """Log at DEBUG level."""
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log at INFO level."""
        self._logger.info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        """Log at WARNING level."""
        self._logger.warn(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log at ERROR level."""
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Log at CRITICAL level."""
        self._logger.critical(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        """ Log at the given level."""
        self._logger.log(level, msg, *args, **kwargs)

