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


"""Text searching functionality."""


__all__ = [
    'AvalonTextSearch'
    ]


class AvalonTextSearch(object):

    """Methods for searching basic or track elements based on
    text matching.
    """

    def __init__(self, album_store, artist_store, genre_store, track_store):
        """Set the backing stores for searching."""
        self._albums = album_store
        self._artists = artist_store
        self._genres = genre_store
        self._tracks = track_store

    def search_albums(self, needle):
        """Search albums by name (case insensitive)."""
        return self._search_elms(self._albums.all(), needle)

    def search_artists(self, needle):
        """Search artists by name (case insensitive)."""
        return self._search_elms(self._artists.all(), needle)

    def search_genres(self, needle):
        """Search genres by name (case insensitive)."""
        return self._search_elms(self._genres.all(), needle)

    def search_tracks(self, needle):
        """Search for tracks that have an album, artist, genre,
        or name or containing the given needle (case insensitive).
        """
        albums = self.search_albums(needle)
        artists = self.search_artists(needle)
        genres = self.search_genres(needle)

        out = set()

        for album in albums:
            out.update(self._tracks.by_album(album.id))
        for artist in artists:
            out.update(self._tracks.by_artist(artist.id))
        for genre in genres:
            out.update(self._tracks.by_genre(genre.id))

        return out.union(self._search_elms(self._tracks.all(), needle))

    def _search_elms(self, elms, needle):
        """Search the name field of the given elements for the
        needle (case insensitive).
        """
        out = set()
        if not elms or not needle:
            return out

        query = needle.lower()
        for elm in elms:
            match = self._search_elm(elm, query)
            if match is not None:
                out.add(match)
                continue
        return out

    def _search_elm(self, elm, needle):
        """Return the element if it matches the needle, None
        otherwise.
        """
        val = getattr(elm, 'name', '').lower()
        if needle in val:
            return elm
        return None

