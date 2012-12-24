# -*- coding: utf-8 -*-
#
# Avalon Music Server
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


"""Methods for accessing request parameters and altering the reponse code."""


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

