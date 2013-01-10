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


import collections
from unicodedata import normalize, category


__all__ = [
    'searchable',
    'strip_accents',
    'AvalonTextSearch',
    'SearchMeta',
    'SearchTrie',
    'TrieNode'
    ]


def searchable(s):
    """Convert an input string to a consistent searchable form by
    removing accents, diaretics, and converting it to lowercase.
    """
    if not s:
        return ''
    return strip_accents(s).lower()


def strip_accents(s):
    """Decompose unicode characters into their base characters so
    that we can return more meaningful search results by not taking
    accents and such into account.

    See http://stackoverflow.com/a/1410365
    """
    return ''.join((c for c in normalize('NFD', unicode(s)) if category(c) != 'Mn'))


class SearchMeta(collections.namedtuple('_SearchMeta', [
    'name',
    'elm'])):

    """Wrapper for a code-folded, searchable, version of a metadata
    element.
    """

    @classmethod
    def from_elm(cls, elm):
        """Construct a new searchable wrapper from the given element.

        The 'name' field of the element is used as the search text after
        having accents and diaretic marks stripped and being converted to
        lowercase.
        """
        return cls(searchable(elm.name), elm)


class TrieNode(object):

    """ """

    def __init__(self):
        """ """
        self.prefix = ''
        self.elements = set()
        self.children = {}

    def __str__(self):
        """ """
        return '<TrieNode prefix: %s>' % self.prefix


class SearchTrie(object):

    """ """

    def __init__(self, node_cls):
        """ """
        self._node_cls = node_cls
        self._root = self._node_cls()

    def add_element(self, term, element):
        """ """
        self._add_element(self._root, term, 0, element)

    def _add_element(self, node, term, i, element):
        """ """
        if i > 0:
            node.elements.add(element)
        if i == len(term):
            return
        char = term[i]
        if char not in node.children:
            next = self._node_cls()
            next.prefix = char
            node.children[char] = next
        else:
            next = node.children[char]
        self._add_element(next, term, i + 1, element)

    def search(self, term):
        """ """
        return self._search(self._root, term, 0)

    def _search(self, node, term, i):
        """ """
        if not term:
            return set()

        if i == len(term):
            return node.elements

        char = term[i]
        if char not in node.children:
            return set()

        if not node.children:
            return node.elements
        return self._search(node.children[char], term, i + 1)


class AvalonTextSearch(object):

    """Methods for searching basic or track elements based on
    text matching.
    """

    def __init__(self, album_store, artist_store, genre_store, track_store):
        """Set the backing stores for searching and use them
        to build a search index for the music collection.
        """
        self._album_store = album_store
        self._artist_store = artist_store
        self._genre_store = genre_store
        self._track_store = track_store

        self._album_search = None
        self._artist_search = None
        self._genre_search = None
        self._track_search = None

        self.reload()

    def reload(self):
        """Rebuild the search indexes for the collection."""
        albums = frozenset(SearchMeta.from_elm(elm) for elm in self._album_store.all())
        artists = frozenset(SearchMeta.from_elm(elm) for elm in self._artist_store.all())
        genres = frozenset(SearchMeta.from_elm(elm) for elm in self._genre_store.all())
        tracks = frozenset(SearchMeta.from_elm(elm) for elm in self._track_store.all())

        self._album_search = SearchTrie(TrieNode)
        self._artist_search = SearchTrie(TrieNode)
        self._genre_search = SearchTrie(TrieNode)
        self._track_search = SearchTrie(TrieNode)

        for meta in albums:
            for term in meta.name.split():
                self._album_search.add_element(term, meta.elm)

        for meta in artists:
            for term in meta.name.split():
                self._artist_search.add_element(term, meta.elm)

        for meta in genres:
            for term in meta.name.split():
                self._genre_search.add_element(term, meta.elm)

        for meta in tracks:
            for term in meta.name.split():
                self._track_search.add_element(term, meta.elm)

    def search_albums(self, needle):
        """Search albums by name (case insensitive)."""
        return self._album_search.search(searchable(needle))

    def search_artists(self, needle):
        """Search artists by name (case insensitive)."""
        return self._artist_search.search(searchable(needle))

    def search_genres(self, needle):
        """Search genres by name (case insensitive)."""
        return self._genre_search.search(searchable(needle))

    def search_tracks(self, needle):
        """Search for tracks that have an album, artist, genre,
        or name or containing the given needle (case insensitive).
        """
        # Search for the needle in albums, artists, and genres separately
        # so that we aren't checking those fields on every track, just the
        # name field for each track.
        albums = self.search_albums(needle)
        artists = self.search_artists(needle)
        genres = self.search_genres(needle)

        out = set()

        for album in albums:
            out.update(self._track_store.by_album(album.id))
        for artist in artists:
            out.update(self._track_store.by_artist(artist.id))
        for genre in genres:
            out.update(self._track_store.by_genre(genre.id))

        return out.union(self._track_search.search(searchable(needle)))


