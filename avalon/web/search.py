# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Text searching functionality for music meta data."""

from __future__ import absolute_import, unicode_literals
from unicodedata import normalize, category
import logging

import avalon.compat
import avalon.log
import avalon.util


__all__ = [
    'searchable',
    'strip_accents',
    'AvalonTextSearch',
    'SearchTrie',
    'TrieNode'
]


def tokenize(text):
    """Get a set of each combination of parts of the given text (delineated
    via whitespace) that an item should be indexed under in a search trie.

    For example, the text "This is giving up" result in a set of the following
    substrings:

    * The entire term: "This is giving up",
    * Each part: "This", "is", "giving", and "up"
    * Each trailing portion: "is giving up", "giving up"

    ``None`` text or text that is all whitespace will result in an empty set.

    :param unicode text: Text to split into tokens for searching in a trie
    :return: Set of substrings that the element corresponding to the input
        text should be indexed under.
    :rtype: set
    """
    if not text:
        return set()

    term = searchable(text)
    parts = term.split()

    if not parts:
        return set()

    tokens = set(parts)
    tokens.add(term)
    # Skipping the first and last elements since they are covered by
    # indexing the entire term and each part of the term (respectively)
    for i in range(1, len(parts) - 1):
        tokens.add(' '.join(parts[i:]))
    return tokens


def searchable(query):
    """Convert an input string to a consistent searchable form by
    removing accents, diaretics, and converting it to lowercase.

    None input will be converted to an empty string.

    :param unicode query: Unicode string to convert to a searchable form
    :return: Normalized searchable unicode string
    :rtype: unicode
    """
    if query is None:
        return ''
    return strip_accents(query).lower()


def strip_accents(query):
    """Decompose unicode characters into their base characters so
    that we can return more meaningful search results by not taking
    accents and such into account.

    See http://stackoverflow.com/a/1410365

    :param unicode query: Lowercase unicode string to remove accents from
    :return: String with only base characters, no access and umlauts
    :rtype: unicode
    """
    chars = []
    for char in normalize('NFD', avalon.compat.to_text(query)):
        if category(char) != 'Mn':
            chars.append(char)
    return ''.join(chars)


# Individual node in the search trie. This object is more complicated than
# it could be in order to save on memory. For example we use the __slots__
# functionality to avoid an extra dictionary per instance (about 280 bytes).
# We store metadata elements for this node locally when there is only one to
# avoid a set object (about 280 bytes). We also store a child node and index
# character locally when there is only one to avoid a dictionary (about 280
# bytes). This may not seem like a lot but it adds up. With my music collection
# of about 6000 songs the search trie ends up with over 130K elements. The
# memory optimizations for the TrieNode class mean the SearchTrie takes up
# 25MB of memory vs 200MB for the naive implementation.
class TrieNode(object):
    """Node in a trie that represents a particular path through
    the trie.

    A node has a set of metadata elements that are considered to
    "match" it and links to child nodes indexed by the next character
    in the path.
    """

    # Avoid creating a dictionary attribute for each instance since
    # there are going to be a lot of them and the memory used by those
    # dictionaries quickly adds up
    __slots__ = (
        '_element', '_elements', '_child_key', '_child_val', '_children')

    def __init__(self):
        """Set initial values for elements and child nodes."""
        self._child_key = None
        self._child_val = None
        self._children = None
        self._element = None
        self._elements = None

    def add_element(self, elm):
        """Add an element to the set of elements at this node.

        :param elm: Element that is considered to match this node
        """
        # Most nodes only have a single element stored at them so we
        # cheat and just store that element locally instead of in a set
        # until we have more than one element since sets are quite large.
        if self._elements is None and self._element is None:
            self._element = elm
        else:
            if self._elements is None:
                self._elements = set([self._element])
                self._element = None
            self._elements.add(elm)

    def get_elements(self):
        """Get the set of all elements at this node.

        :return: All elements that are considered to match this node
        :rtype: set
        """
        if self._element is not None:
            return set([self._element])
        if self._elements is not None:
            return set(self._elements)
        return set()

    def add_child(self, char, node):
        """Add a child node to this node indexed by the given character.

        :param unicode char: Character that represents the path to the child
            of this node.
        :param TrieNode node: Child node of this node that represents the next
            step in this trie.
        """
        # Since most nodes only have a single child, we cheat and just store
        # the character and child node locally instead of using a dictionary
        # since dictionaries are quite large. We only use a dictionary for
        # children if there is more than one.
        if self._children is None and self._child_val is None:
            self._child_key = char
            self._child_val = node
        else:
            if self._children is None:
                self._children = {self._child_key: self._child_val}
                self._child_key = self._child_val = None
            self._children[char] = node

    def get_children(self):
        """Get a dictionary of the child nodes indexed by a character.

        :return: Child nodes indexed by the character that indicates a
            path through the trie to that child.
        :rtype: dict
        """
        if self._child_val is not None:
            return {self._child_key: self._child_val}
        if self._children is not None:
            return dict(self._children)
        return {}


class SearchTrie(object):
    """Search trie structure with functionality for building an index
    for text matching and querying it.

    Insert and lookup performance should be O(m) where m is the length
    of the term being inserted or looked up. No normalization is done
    when terms are added to the trie or when the trie is queried, this
    is expected to be done by the caller.

    The SearchTrie is not inherently threadsafe. However, if none of the
    mutator methods are called [.add()] the read methods [.search(), .size()]
    are safe to be called by multiple threads.
    """

    def __init__(self, node_factory):
        """Set the factory to use for individual nodes in the trie and
        build the root node.
        """
        self._node_factory = node_factory
        self._size = 0
        self._root = self._new_node()

    def _new_node(self):
        """Create a new node and increment the node counter."""
        self._size += 1
        return self._node_factory()

    def __len__(self):
        """ Return the number of nodes in this search trie."""
        return self._size

    def add(self, term, element):
        """Add a metadata element to the trie indexed using the given term.

        The term is expected to be normalized using the same method that will
        be used for searches against the trie.

        :param unicode term: Search term to index the given element under.
        :param element: Element to add to the trie under the given term.
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
            node.add_element(element)
        if i == len(term):
            return

        char = term[i]
        children = node.get_children()
        if char not in children:
            child = self._new_node()
            node.add_child(char, child)
        else:
            child = children[char]
        self._add(child, term, i + 1, element)

    def search(self, term):
        """Search for metadata elements that match the given term, returning a
        set of matching elements, and an empty set if there are no matches.

        The term is expected to be normalized using the same method that was
        used to build the trie.

        :param unicode term: Search term to use to find matching elements.
        :return: Set of all elements in the trie matching the term.
        :rtype: set
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
            return node.get_elements()

        char = term[i]
        children = node.get_children()
        if char not in children:
            # We're not at a leaf node or the end of the search
            # term but none of the children of the current node
            # match, no results
            return set()

        # Otherwise, continue searching at the next node
        return self._search(children[char], term, i + 1)


class AvalonTextSearch(object):
    """Reloadable, thread-safe, in-memory store of search indexes for
    albums, artists, genres, and songs.

    Search indexes are constructed when the .reload() method is called.

    Values used to build the indexes are normalized via the searchable()
    function as well as any queries against the indexes.
    """
    _logger = avalon.log.get_error_log()

    def __init__(self, album_store, artist_store, genre_store,
                 track_store, trie_factory):
        """Set the backing stores and new search trie factory for
        searching and use them to build a search index for the music
        collection.

        The trie factory is expected to return search tries with the
        same interface as the :class:`SearchTrie` class above. These
        instances may be mutable but will not be modified after they
        are constructed in the .reload() method.

        Note that meta data from each of the stores will be loaded and
        the tries will be constructed immediately upon instantiation of
        this class.
        """
        self._album_store = album_store
        self._artist_store = artist_store
        self._genre_store = genre_store
        self._track_store = track_store
        self._trie_factory = trie_factory

        self._album_search = None
        self._artist_search = None
        self._genre_search = None
        self._track_search = None

    def __len__(self):
        return len(self._album_search) + \
               len(self._artist_search) + \
               len(self._genre_search) + \
               len(self._track_search)

    def reload(self):
        """Rebuild the search indexes for the collection and return this object."""
        album_search = self._trie_factory()
        artist_search = self._trie_factory()
        genre_search = self._trie_factory()
        track_search = self._trie_factory()

        self._add_all_to_tree(self._album_store.get_all(), album_search)
        self._add_all_to_tree(self._artist_store.get_all(), artist_search)
        self._add_all_to_tree(self._genre_store.get_all(), genre_search)
        self._add_all_to_tree(self._track_store.get_all(), track_search)

        self._album_search = album_search
        self._artist_search = artist_search
        self._genre_search = genre_search
        self._track_search = track_search

        # Check if DEBUG is enabled since getting memory usage is slow
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                'Albums search trie using %s mb', avalon.util.get_size_in_mb(album_search))
            self._logger.debug(
                'Artist search trie using %s mb', avalon.util.get_size_in_mb(artist_search))
            self._logger.debug(
                'Genre search trie using %s mb', avalon.util.get_size_in_mb(genre_search))
            self._logger.debug(
                'Track search trie using %s mb', avalon.util.get_size_in_mb(track_search))

        return self

    @staticmethod
    def _add_all_to_tree(elms, trie):
        """Add a normalized version of the name of each of the given
        elements to the search trie.
        """
        for elm in elms:
            tokens = tokenize(elm.name)
            for token in tokens:
                trie.add(token, elm)

    def search_albums(self, needle):
        """Search albums by name (case insensitive).

        :param unicode needle: Needle to search album names for
        :return: Set of albums :class:`avalon.elms.IdNameElm` that match
        :rtype: set
        """
        return self._album_search.search(searchable(needle))

    def search_artists(self, needle):
        """Search artists by name (case insensitive).

        :param unicode needle: Needle to search album names for
        :return: Set of artist :class:`avalon.elms.IdNameElm` that match
        :rtype: set
        """
        return self._artist_search.search(searchable(needle))

    def search_genres(self, needle):
        """Search genres by name (case insensitive).

        :param unicode needle: Needle to search genre names for
        :return: Set of genre :class:`avalon.elms.IdNameElm` that match
        :rtype: set
        """
        return self._genre_search.search(searchable(needle))

    def search_tracks(self, needle):
        """Search for tracks that have an album, artist, genre,
        or name or containing the given needle (case insensitive).

        :param unicode needle: Needle to search for in track names,
            album names, artist names, and genre names
        :return: Set of track :class:`avalon.elms.TrackElm` that match
        :rtype: set
        """
        # Search for the needle in albums, artists, and genres separately
        # so that we only check the name of an element for matches no matter
        # what type it is.
        albums = self.search_albums(needle)
        artists = self.search_artists(needle)
        genres = self.search_genres(needle)

        out = set()

        for album in albums:
            out.update(self._track_store.get_by_album(album.id))
        for artist in artists:
            out.update(self._track_store.get_by_artist(artist.id))
        for genre in genres:
            out.update(self._track_store.get_by_genre(genre.id))

        return out.union(self._track_search.search(searchable(needle)))
