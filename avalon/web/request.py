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


"""Methods for accessing request parameters."""

import uuid

import avalon.err
import avalon.exc


__all__ = [
    'Parameters'
]


class Parameters(object):
    """Logic for accessing query string parameters of interest."""

    valid = frozenset(
        ['album', 'album_id', 'artist', 'artist_id', 'direction',
         'order', 'genre', 'genre_id', 'limit', 'offset', 'query'])

    def __init__(self, query_params):
        """Set the query string params to use."""
        self._query_params = query_params

    def get_int(self, field, default=None):
        """Return the value of the field as an int, raising an error if
        it isn't a valid field or cannot be converted to an int, and
        returning None if the field isn't in the query string.
        """
        val = self.get(field)
        if val is None:
            return default

        try:
            return int(val)
        except (ValueError, TypeError):
            raise avalon.exc.InvalidParameterError(
                avalon.err.ERROR_INVALID_FIELD_VALUE(field))

    def get_uuid(self, field, default=None):
        """Return the value of the field as a UUID, raising an error
        if it isn't a valid field or cannot be converted to a UUID, and
        returning None if the field isn't in the query string.
        """
        val = self.get(field)
        if val is None:
            return default

        try:
            return uuid.UUID(val)
        except ValueError:
            raise avalon.exc.InvalidParameterError(
                avalon.err.ERROR_INVALID_FIELD_VALUE(field))

    def get(self, field, default=None):
        """Return the value of the field, raising an error if it isn't
        a valid field, raising an error if there are multiple values for
        the field, and returning None if the field isn't in the query 
        string.
        """
        if field not in self.valid:
            raise avalon.exc.InvalidParameterError(
                avalon.err.ERROR_INVALID_FIELD(field))

        if field not in self._query_params:
            return default

        value = self._query_params[field]

        # TODO: Support multiple values for each param
        if isinstance(value, list):
            raise avalon.exc.InvalidParameterError(
                avalon.err.ERROR_DUPLICATE_FIELD_VALUE(field))
        return value

