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


"""Errors thrown by the Avalon music server."""

__all__ = [
    'ApiError',
    'AvalonError',
    'ConnectionError',
    'DatabaseError',
    'InvalidParameterError',
    'OperationalError',
    'PermissionError',
    'ServerNotReadyError'
]


class AvalonError(Exception):
    """Base for all exceptions."""

    def __init__(self, msg, err=None):
        """Set the error message and optional original error."""
        self.message = msg
        self.err = err

    def __str__(self):
        """Return a string representation of this error."""
        msg = self.message
        if None is not self.err:
            msg += ': %s' % str(self.err)
        return msg

    @property
    def name(self):
        """The name of this error class."""
        return self.__class__.__name__


class DatabaseError(AvalonError):
    """There was an error performing an operation on the database."""
    pass


class ConnectionError(DatabaseError):
    """There was an error connecting to the database."""
    pass


class OperationalError(DatabaseError):
    """There was an error performing an operation on the database
    due to some external factor, something out of our control.
    """
    pass


class PermissionError(AvalonError):
    """We don't have the required permission."""
    pass


class ApiError(AvalonError):
    """Base for all errors relating to invalid API requests."""

    error_name = None
    """Parsable name of the error that occurred."""

    http_code = None
    """HTTP status code that should be set when this error occurs."""


class InvalidParameterError(ApiError):
    """An invalid parameter or parameter value was given."""

    error_name = "INVALID_PARAMETER_ERROR"

    http_code = 400


class ServerNotReadyError(ApiError):
    """The API server is not ready to handle requests."""

    error_name = "SERVER_NOT_READY_ERROR"

    http_code = 503
