# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2013 TSH Labs <projects@tshlabs.org>
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


"""Methods for accessing request parameters and altering the reponse code."""

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

        if isinstance(value, list):
            raise avalon.exc.InvalidParameterError(
                avalon.err.ERROR_DUPLICATE_FIELD_VALUE(field))
        return value

