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


"""Errors thrown by the Avalon music server."""


__all__ = [
    'ApiError',
    'AvalonError',
    'ConnectionError',
    'DatabaseError',
    'InvalidParameterError',
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
            msg += ': %s' % self.err.message
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


class PermissionError(AvalonError):
    """We don't have the required permission."""
    pass


class ApiError(AvalonError):
    """Base for all errors relating to invalid API requests."""
    pass


class InvalidParameterError(ApiError):
    """An invalid parameter or parameter value was given."""
    pass


class ServerNotReadyError(ApiError):
    """The API server is not ready to handle requests."""
    pass

