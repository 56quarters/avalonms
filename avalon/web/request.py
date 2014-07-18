# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Methods for accessing request parameters."""

from __future__ import unicode_literals
import uuid

import avalon.exc


__all__ = [
    'Parameters'
]


class Parameters(object):
    """Logic for accessing query string parameters of interest."""

    valid = frozenset(
        ['album', 'album_id', 'artist', 'artist_id', 'direction',
         'order', 'genre', 'genre_id', 'limit', 'offset', 'query'])

    def __init__(self, request):
        """Set the query string params to use."""
        self._request = request

    def get_int(self, field, default=None):
        """Return the value of the field as an int, raising an error if
        it isn't a valid field or cannot be converted to an int, and
        returning None if the field isn't in the query string.

        :param unicode field: Field to get the value of
        :param default: Default valid if the field is not present
        :return: The valid of the field as an int or the default value
        :rtype: int
        :raises avalon.exc.InvalidParameterNameError: If the given field is
            not a valid recognized field
        :raises avalon.exc.InvalidParameterTypeError: If there is more than a
            single value for the field or the given value cannot be converted
            to an integer
        """
        val = self.get(field)
        if val is None:
            return default

        try:
            return int(val)
        except (ValueError, TypeError):
            raise avalon.exc.InvalidParameterTypeError(
                "Invalid field value for integer field {field}: '{value}'",
                field=field, value=val)

    def get_uuid(self, field, default=None):
        """Return the value of the field as a UUID, raising an error
        if it isn't a valid field or cannot be converted to a UUID, and
        returning None if the field isn't in the query string.

        :param unicode field: Field to get the value of
        :param default: Default valid if the field is not present
        :return: The valid of the field as a UUID or the default value
        :rtype: uuid.UUID
        :raises avalon.exc.InvalidParameterNameError: If the given field is
            not a valid recognized field
        :raises avalon.exc.InvalidParameterTypeError: If there is more than a
            single value for the field or the given value cannot be converted
            to a valid UUID
        """
        val = self.get(field)
        if val is None:
            return default

        try:
            return uuid.UUID(val)
        except ValueError:
            raise avalon.exc.InvalidParameterTypeError(
                "Invalid field value for UUID field {field}: '{value}'",
                field=field, value=val)

    def get(self, field, default=None):
        """Return the value of the field, raising an error if it isn't
        a valid field, raising an error if there are multiple values for
        the field, and returning None if the field isn't in the query 
        string.

        :param unicode field: Field to get the value of
        :param default: Default valid if the field is not present
        :return: The valid of the field or the default value
        :raises KeyError: If the given field is not a valid recognized field
        :raises avalon.exc.InvalidParameterTypeError: If there is more than a
            single value for the field
        """
        if field not in self.valid:
            # We're raising a KeyError here (instead of a subclass
            # of ApiError) since this isn't something that can be
            # triggered by user input, only bugs in Avalon.
            raise KeyError("Invalid field name '%s'" % field)

        if field not in self._request.args:
            return default

        value = self._request.args[field]

        # TODO: Support multiple values for each param
        if isinstance(value, list):
            raise avalon.exc.InvalidParameterTypeError(
                "Multiple values for field '{field}' are not supported",
                field=field)
        return value
