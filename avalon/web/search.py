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
    return ''.join(
        (c for c in normalize('NFD', unicode(s)) if category(c) != 'Mn'))


class TrieNode(object):

    """Node in a trie that represents a particular path through
    the trie.

    A node has a set of metadata elements that are considered to
    "match" it and links to child nodes indexed by the next character
    in the path.
    """

    def __init__(self):
        """Set initial values for the prefix, elements, and child nodes."""
        self.prefix = ''
        self.elements = set()
        self.children = {}

    def __str__(self):
        """String representation of the node."""
        return '<TrieNode prefix: %s>' % self.prefix


class SearchTrie(object):

    """Search trie structure with functionality for building an index
    for text matching and querying it.

    Insert and lookup performance should be O(m) where m is the length
    of the term being inserted or looked up. No normalization is done
    when terms are added to the trie or when the trie is queried, this
    is expected to be done by the caller.
    """

    def __init__(self, node_cls):
        """Set the class to use for individual nodes in the trie and
        build the root node.
        """
        self._node_cls = node_cls
        self._root = self._node_cls()

    def add(self, term, element):
        """Add a metadata element to the trie indexed using the given term.

        The term is expected to be normalized using the same method that will
        be used for searches against the trie.
        """
        self._add(self._root, term, 0, element)

    def _add(self, node, term, i, element):
        """Recursively construct nodes in a trie for the given term and metadata
        element, adding the element to every intermediate node along the way.
        """
        if i > 0:
            # If this isn't the root node add the element to the
            # node since it will be considered a match for the
            # current prefix
            node.elements.add(element)
        if i == len(term):
            return
        char = term[i]
        if char not in node.children:
            child = self._node_cls()
            child.prefix = char
            node.children[char] = child
        else:
            child = node.children[char]
        self._add(child, term, i + 1, element)

    def search(self, term):
        """Search for metadata elements that match the given term, returning a
        set of matching elements, and an empty set if there are no matches.

        The term is expected to be normalized using the same method that was
        used to build the trie.
        """
        return self._search(self._root, term, 0)

    def _search(self, node, term, i):
        """Recursively search down from the given node for the next
        node based on the position i being examined in the given term.
        """
        if not term:
            # No search term, no results
            return set()

        if i == len(term):
            # We hit the end of the search term, everything at
            # the current node is a match for the term
            return node.elements

        char = term[i]
        if char not in node.children:
            # We're not at a leaf node or the end of the search
            # term but none of the children of the current node
            # match, no results
            return set()

        if not node.children:
            # Leaf node of the trie, everything at the current
            # node is a match for the term.
            return node.elements

        # Otherwise, continue searching at the next node
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
        album_search = SearchTrie(TrieNode)
        artist_search = SearchTrie(TrieNode)
        genre_search = SearchTrie(TrieNode)
        track_search = SearchTrie(TrieNode)

        self._add_all_to_tree(self._album_store.all(), album_search)
        self._add_all_to_tree(self._artist_store.all(), artist_search)
        self._add_all_to_tree(self._genre_store.all(), genre_search)
        self._add_all_to_tree(self._track_store.all(), track_search)

        self._album_search = album_search
        self._artist_search = artist_search
        self._genre_search = genre_search
        self._track_search = track_search

    def _add_all_to_tree(self, elms, trie):
        """Add a normalized version of the name of each of the given
        elements to the search trie.
        """
        for elm in elms:
            for term in searchable(elm.name).split():
                trie.add(term, elm)

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

