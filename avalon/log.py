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


"""Simple logging wrapper."""


import functools
import logging
import sys

import cherrypy

import avalon.exc


__all__ = [
    'wrap_permission_errors',
    'AvalonLog',
    'AvalonLogConfig',
    'AvalonLogPlugin'

    ]




def error_decorator(func):
    """Create a decorator that turns IOError permission
    issues into our PermissionError, reraise all other types.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except IOError, e:
            if not avalon.util.is_perm_error(e):
                # If this isn't a permission related error 
                # simply reraise the exception untouched.
                raise
            raise avalon.exc.PermissionError(
                'Insufficient permission to create or open '
                'log [%s]' %  e.filename, e)
    return wrapper


class AvalonLogConfig(object):

    """Configuration for the logger."""

    def __init__(self):
        self.log_root = None
        self.access_path = None
        self.error_path = None
        self.log_level = logging.INFO


class AvalonLog(object):

    """Handle setting up log formatters and handlers based
    on configuration settings.
    """

    _access_fmt = '%(message)s'
    
    _error_fmt = '%(levelname)s %(asctime)s %(message)s'

    _date_fmt = '%Y-%m-%d %H:%M:%S'

    def __init__(self, config):
        """Set the path to the log file or None to use stderr."""
        self._log_root = config.log_root
        self._access_path = config.access_path
        self._error_path = config.error_path
        self._level = config.log_level

        self._logger = None
        self._handlers = []

        self.reload()
        
    def get_open_fds(self):
        """Get the file number of any open log files."""
        return [
            handler.stream.fileno() for handler in self._handlers if handler.stream]

    def get_open_paths(self):
        """Get the file path of any open log files."""
        return [
            handler.stream.name for handler in self._handlers if handler.stream]

    def reload(self):
        """ Configure logging and install our own handlers."""
        # Clear any existing handlers we've installed
        for handler in self._handlers:
            self._log_root.access_log.removeHandler(handler)
        for handler in self._handlers:
            self._log_root.error_log.removeHandler(handler)
        
        self._handlers = []
        self._setup_access_log()
        self._setup_error_log()

        # Application logging uses the error log
        self._logger = self._log_root.error_log

    @error_decorator
    def _setup_access_log(self):
        """Add a configured handler to the access log of the logging root."""
        if self._access_path is None:
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = logging.FileHandler(self._access_path)
        handler.setFormatter(logging.Formatter(self._access_fmt))

        self._log_root.access_log.addHandler(handler)
        self._handlers.append(handler)

    @error_decorator
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


class AvalonLogPlugin(cherrypy.process.plugins.SimplePlugin):

    """Adapter to allow our logger to be used as a CherryPy
    plugin for the bus system.

    Supports the 'graceful' and 'log' channels.
    """

    def __init__(self, bus, log):
        super(AvalonLogPlugin, self).__init__(bus)
        self._log = log

    def graceful(self):
        """Configure and reinstall our log handlers (including
        reopening log files.
        """
        self._log.info("Reopening logs...")
        self._log.reload()
        self._log.info("Logs reopened")

    # Set the priority for graceful higher than the default so
    # that we can ensure we have a valid log handle when any
    # other graceful subscribers run.
    graceful.priority = 45

    def log(self, msg, level):
        """Log the message at the desired level."""
        # NOTE: CherryPy argument order is reversed compared
        # to the logging module.
        self._log.log(level, msg)
    
        
