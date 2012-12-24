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


""" Text searching functionality."""


__all__ = [
    'AvalonTextSearch'
    ]


class AvalonTextSearch(object):

    """Methods for searching basic or track elements based on
    text matching.
    """

    basic_fields = frozenset(['name'])

    track_fields = frozenset(['name', 'album', 'artist', 'genre'])

    def search_basic(self, elms, needle):
        """Search the text fields of album, artist, or genre elements
        for the given needle after converting all value to lowercase
        (case insensitive comparison).
        """
        return self._search_elms(elms, needle, self.basic_fields)

    def search_tracks(self, elms, needle):
        """Search the text fields of track elements for the given
        needle after converting all values to lowercase (case
        insensitive comparison).
        """
        return self._search_elms(elms, needle, self.track_fields)

    def _search_elms(self, elms, needle, fields):
        """Search fields of the given elements for the
        needle (after all values have been converted to
        lowercase).
        """
        out = set([])
        if not elms or not needle:
            return out

        query = needle.lower()
        for elm in elms:
            match = self._search_fields(elm, query, fields)
            if match is not None:
                out.add(match)
                continue
        return out

    def _search_fields(self, elm, needle, fields):
        """Return the given element if any fields match
        the needle, None otherwise.
        """
        for field in fields:
            val = getattr(elm, field, '').lower()
            if needle in val:
                return elm
        return None

