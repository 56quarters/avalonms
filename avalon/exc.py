# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Errors thrown by the Avalon music server."""

from __future__ import absolute_import, unicode_literals

__all__ = [
    'ApiError',
    'AvalonError',
    'ConnectionError',
    'DatabaseError',
    'InvalidParameterNameError',
    'InvalidParameterTypeError',
    'InvalidParameterValueError',
    'OperationalError',
    'PermissionError',
    'ServiceMisconfiguredError',
    'ServiceUnavailableError',
    'ServiceUnknownError'
]


class AvalonError(Exception):
    """Base for all exceptions.

    :ivar str message:
    :ivar Exception err:
    """

    def __init__(self, msg):
        """Set the error message."""
        super(AvalonError, self).__init__()
        self.message = msg

    def __str__(self):
        """Return a string representation of this error."""
        return self.message

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
    """Base for all errors relating to invalid API requests.

    :ivar str message: Message describing the error that occurred.
    :ivar dict payload: Key-value pairs that contain needed information
        for reconstructing a message describing this error.
    :cvar int code: Unique code for this error condition that a client
        might use to take some action on.
    :cvar str message_key: Unique string that can be used to look.
        up some sort of alternate message to be used for this error.
    :cvar int http_code: HTTP status code to set when rendering the
        error response.
    """
    code = None
    message_key = None
    http_code = None

    def __init__(self, msg, **kwargs):
        super(ApiError, self).__init__(msg.format(**kwargs))
        self.payload = kwargs


class ServiceUnknownError(ApiError):
    """The service encountered an unknown error."""
    code = 1
    message_key = 'avalon.service.error.unknown'
    http_code = 500


class ServiceUnavailableError(ApiError):
    """The service is currently unavailable for unknown reasons."""
    code = 2
    message_key = 'avalon.service.error.unavailable'
    http_code = 503


class ServiceMisconfiguredError(ApiError):
    """The service is misconfigured and currently unavailable."""
    code = 3
    message_key = 'avalon.service.error.misconfigured'
    http_code = 503


class InvalidParameterNameError(ApiError):
    """A parameter does not correspond to any known parameters."""
    code = 100
    message_key = 'avalon.service.error.invalid_input_name'
    http_code = 400


class InvalidParameterTypeError(ApiError):
    """A parameter is of an invalid type."""
    code = 101
    message_key = 'avalon.service.error.invalid_input_type'
    http_code = 400


class InvalidParameterValueError(ApiError):
    """A parameter contains a semantically invalid value."""
    code = 102
    message_key = 'avalon.service.error.invalid_input_value'
    http_code = 400
