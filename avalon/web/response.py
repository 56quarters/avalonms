# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Methods for converting results or errors to a serializable format
and rendering them as JSON.
"""

from __future__ import unicode_literals
import uuid

import flask
# NOTE: We use simplejson explicitly here instead of the stdlib
# json module since simplejson renders named tuples as JSON
# objects and the stdlib json renders them as JSON lists.
import simplejson
from avalon import six


__all__ = [
    'render',
    'AvalonJsonDecoder',
    'AvalonJsonEncoder',
    'ServiceResponse',
    'ApiErrorCode'
]

AvalonJsonDecoder = simplejson.JSONDecoder


class AvalonJsonEncoder(simplejson.JSONEncoder):
    """Avalon specific JSON encoder."""

    # Disable warning about hidden method since it's overridden on purpose
    # pylint: disable=method-hidden
    def default(self, o):
        if isinstance(o, uuid.UUID):
            return six.text_type(o)
        if isinstance(o, ApiErrorCode):
            return o.to_dict()
        return super(AvalonJsonEncoder, self).default(o)


def render(results=None, error=None):
    """Factory function for a RequestOutput object with optional
    error and success payload parameters that uses :func:`flask.jsonify`
    to render the results or error as a JSON object.

    :param results: Results to include as the success payload
        or None
    :param avalon.exc.ApiError: Exception to render as the error
        payload or None
    :return: The result payload or error as a flask response
    :rtype: flask.Response
    :raises ValueError: If both results and error are included
    """
    if results is not None and error is not None:
        raise ValueError("Only results or error can be specified")

    output = ServiceResponse()
    if results is not None:
        output.success = results
    if error is not None:
        output.errors = [ApiErrorCode.from_api_error(error)]
    return flask.jsonify(**output.to_dict())


class ServiceResponse(object):
    """Class that acts as the top level object returned to clients in
    response to service requests.

    :ivar object success: The payload if the call was successful, None
        otherwise
    :ivar list errors: List of :class:`ApiErrorCode` instances that indicate
        why the request failed. This will be empty if the request was successful
    :ivar list warnings: List of warning messages (strings) that were generated
        during the course of the request. These are typically not meant to be
        user facing.
    """

    def __init__(self):
        self.success = None
        self.errors = []
        self.warnings = []

    def to_dict(self):
        """Return this object as a :class:`dict` so it can be serialized
        to JSON.

        :return: This object as a dictionary
        :rtype: dict
        """
        return {
            'success': self.success,
            'errors': self.errors,
            'warnings': self.warnings
        }


class ApiErrorCode(object):
    """Class that represents the client representation an expected error
    that may occur in the course of handling a service request.

    :ivar int code: Unique code that identifies this error condition to
        consumers
    :ivar str message: Developer-facing message about the error condition
    :ivar str message_key: Key that corresponds to the error message that
        could be used by consumers to localize the error message
    :ivar dict payload: Key-value pairs of any information needed to
        reconstruct a useful message describing this error condition
    """

    def __init__(self):
        self.code = None
        self.message = None
        self.message_key = None
        self.payload = None

    def to_dict(self):
        """Return this object as a :class:`dict` so it can be serialized
        to JSON.

        :return: This object as a dictionary
        :rtype: dict
        """
        return {
            'code': self.code,
            'message': self.message,
            'message_key': self.message_key,
            'payload': self.payload
        }

    @classmethod
    def from_api_error(cls, e):
        """Create a new :class:`ApiErrorCode` instance from an
        :class:`avalon.exc.ApiError` exception.

        :param avalon.exc.ApiError e: Exception to create the
            error from
        :return: An API error code representing the given exception
        :rtype: ApiErrorCode
        """
        err = cls()
        err.code = e.code
        err.message = e.message
        err.message_key = e.message_key
        err.payload = e.payload
        return err
