# -*- coding: utf-8 -*-
#

from __future__ import absolute_import, unicode_literals
import uuid

import mock
import pytest
import avalon.cache
import avalon.elms
import avalon.web.search


class TestTokenize(object):
    def test_tokenize_success(self):
        """Test the logic used for splitting album, artist, etc. names up."""
        tokens = avalon.web.search.tokenize("Die While We're Young")

        # Whole term
        assert "die while we're young" in tokens

        # Each part
        assert "die" in tokens
        assert "while" in tokens
        assert "we're" in tokens
        assert "young" in tokens

        # Combinations of tailing parts
        assert "while we're young" in tokens
        assert "we're young" in tokens

    def test_tokenize_none(self):
        """Test that we get an expeted empty set with None input."""
        tokens = avalon.web.search.tokenize(None)
        assert 0 == len(tokens)

    def test_tokenize_empty_string(self):
        """Test that we get an expected empty set with no input."""
        tokens = avalon.web.search.tokenize("")
        assert 0 == len(tokens)

    def test_tokenize_all_whitespace(self):
        """Test that we get an expected empty set with whitespace input."""
        tokens = avalon.web.search.tokenize("         \n ")
        assert 0 == len(tokens)

    def test_tokenize_single_word(self):
        """Test that a single word doesn't result in duplicate tokens."""
        tokens = avalon.web.search.tokenize("Reject")
        assert "reject" in tokens
        assert 1 == len(tokens)


class TestSearchable(object):
    def test_searchable_no_input(self):
        """Ensure that None input is handle reasonably."""
        assert '' == avalon.web.search.searchable(None)

    def test_searchable_umlaut_mixed_case(self):
        """Ensure that umlauts are removed and case is converted."""
        word = 'Düsseldorf'
        assert 'dusseldorf' == avalon.web.search.searchable(word)

    def test_searchable_accent_mixed_case(self):
        """Ensure that accents are removed and case is converted."""
        word = 'Verás'
        assert 'veras' == avalon.web.search.searchable(word)

    def test_searchable_accent_mixed_case_whitespace(self):
        """Ensure that accents are removed, case is converted, and leading
        and trailing whitespace is stripped.
        """
        word = ' Verás '
        assert 'veras' == avalon.web.search.searchable(word)


class TestStripAccents(object):
    def test_strip_accents_umlaut(self):
        """Ensure that umlauts are removed and case is preserved."""
        word = 'Düsseldorf'
        assert 'Dusseldorf' == avalon.web.search.strip_accents(word)

    def test_strip_accents_accent(self):
        """Ensure that accents are removed and case is preserved."""
        word = 'Verás'
        assert 'Veras' == avalon.web.search.strip_accents(word)


class TestTrieNode(object):
    def test_elements_empty(self):
        """Ensure that trie notdes are initially empty."""
        node = avalon.web.search.TrieNode()
        assert 0 == len(node.get_elements())

    def test_one_element(self):
        """Ensure that the `add_element` method works for a single element."""
        node = avalon.web.search.TrieNode()
        node.add_element(123)

        elms = node.get_elements()
        assert 1 == len(elms)
        assert 123 in elms

    def test_two_elements(self):
        """Ensure that the `add_element` method works for two elements."""
        node = avalon.web.search.TrieNode()
        node.add_element(123)
        node.add_element(456)

        elms = node.get_elements()
        assert 2 == len(elms)
        assert 123 in elms
        assert 456 in elms

    def test_children_empty(self):
        """Ensure that trie nodes initially have no children."""
        node = avalon.web.search.TrieNode()
        assert 0 == len(node.get_children())

    def test_one_child(self):
        """Ensure that a single child added is indexed correctly."""
        node = avalon.web.search.TrieNode()
        child = avalon.web.search.TrieNode()

        node.add_child('a', child)
        children = node.get_children()
        assert 1 == len(children)
        assert 'a' in children

    def test_two_children(self):
        """Ensure that two children added are indexed correctly."""
        node = avalon.web.search.TrieNode()
        child1 = avalon.web.search.TrieNode()
        child2 = avalon.web.search.TrieNode()

        node.add_child('a', child1)
        node.add_child('b', child2)
        children = node.get_children()
        assert 2 == len(children)
        assert 'a' in children
        assert 'b' in children


def _dummy_node_factory():
    return _DummyNode()


class _DummyNode(object):
    def __init__(self):
        self._elements = set()
        self._children = {}

    def add_element(self, elm):
        self._elements.add(elm)

    def get_elements(self):
        return set(self._elements)

    def add_child(self, char, node):
        self._children[char] = node

    def get_children(self):
        return dict(self._children)


class TestSearchTrie(object):
    def test_init_creates_root(self):
        """Ensure that the initial construction of the trie creates
        a root node and that the size of this empty trie is 1.
        """
        trie = avalon.web.search.SearchTrie(_dummy_node_factory)
        assert trie._root is not None
        assert trie._size == 1

    def test_add_creates_initial_nodes(self):
        """Ensure that adding a single term to the trie builds additional
        nodes off of the root node and that they are indexed as expected.
        """
        trie = avalon.web.search.SearchTrie(_dummy_node_factory)
        trie.add('foo', object())

        assert trie._size == 4
        assert 'f' in trie._root.get_children()
        node1 = trie._root.get_children()['f']
        assert 'o' in node1.get_children()
        node2 = node1.get_children()['o']
        assert 'o' in node2.get_children()

    def test_add_with_existing_nodes(self):
        """Ensure that adding another node after adding the first one
        correctly navigates the existing nodes to append new ones.
        """
        trie = avalon.web.search.SearchTrie(_dummy_node_factory)
        trie.add('ab', object())
        trie.add('ac', object())

        assert trie._size == 4
        first_level = trie._root.get_children()
        assert len(first_level) == 1
        assert 'a' in first_level

        second_level = first_level['a'].get_children()
        assert len(second_level) == 2
        assert 'b' in second_level
        assert 'c' in second_level

    def test_search_no_term(self):
        """Ensure that an empty or None search term results in
        no results from a search.
        """
        trie = avalon.web.search.SearchTrie(_dummy_node_factory)
        results1 = trie.search('')
        assert 0 == len(results1)
        results2 = trie.search(None)
        assert 0 == len(results2)

    def test_search_end_of_term(self):
        """Ensure that when we get to the end of search term
        all elements at the current node are considered matches.
        """
        trie = avalon.web.search.SearchTrie(_dummy_node_factory)
        root = trie._root
        first = _dummy_node_factory()
        second = _dummy_node_factory()
        third = _dummy_node_factory()

        first.add_element('bit')
        second.add_element('bit')
        third.add_element('bit')

        root.add_child('b', first)
        first.add_child('i', second)
        second.add_child('t', third)

        results = trie.search('b')
        assert 1 == len(results)
        for elm in results:
            assert 'bit' == elm

    def test_search_no_match(self):
        """Ensure that a term that does not entirely match the terms
        stored in the trie results in no results.
        """
        trie = avalon.web.search.SearchTrie(_dummy_node_factory)
        root = trie._root
        first = _dummy_node_factory()
        second = _dummy_node_factory()
        third = _dummy_node_factory()

        first.add_element('bit')
        second.add_element('bit')
        third.add_element('bit')

        root.add_child('b', first)
        first.add_child('i', second)
        second.add_child('t', third)

        results = trie.search('big')
        assert 0 == len(results)

    def test_search_multiple_matches(self):
        """Ensure that we can query specific terms store in the
        trie as well as use a common prefix for multiple terms.
        """
        trie = avalon.web.search.SearchTrie(_dummy_node_factory)
        root = trie._root
        first = _dummy_node_factory()
        second = _dummy_node_factory()
        third = _dummy_node_factory()
        forth = _dummy_node_factory()

        first.add_element('bit')
        first.add_element('big')

        second.add_element('bit')
        second.add_element('big')

        third.add_element('bit')
        forth.add_element('big')

        root.add_child('b', first)
        first.add_child('i', second)
        second.add_child('t', third)
        second.add_child('g', forth)

        results1 = trie.search('bit')
        assert 1 == len(results1)

        results2 = trie.search('big')
        assert 1 == len(results2)

        results3 = trie.search('bi')
        assert 2 == len(results3)


@pytest.fixture
def album_store():
    return mock.Mock(spec=avalon.cache.AlbumStore)


@pytest.fixture
def artist_store():
    return mock.Mock(spec=avalon.cache.ArtistStore)


@pytest.fixture
def genre_store():
    return mock.Mock(spec=avalon.cache.GenreStore)


@pytest.fixture
def track_store():
    return mock.Mock(spec=avalon.cache.TrackStore)


def trie_factory():
    return avalon.web.search.SearchTrie(
        node_factory=avalon.web.search.TrieNode)


class TestAvalonTextSearch(object):
    def setup(self):
        self.album_id = uuid.UUID('0c254968-90cb-56d5-9af8-7bf21962fa42')
        self.artist_id = uuid.UUID('1212bd9c-5fb5-524a-b748-7ece590f8875')
        self.genre_id = uuid.UUID('8794d7b7-fff3-50bb-b1f1-438659e05fe5')

        self.album = avalon.elms.IdNameElm(
            id=self.album_id,
            name='So Long And Thanks For All the Shoes')

        self.artist = avalon.elms.IdNameElm(
            id=self.artist_id,
            name='NOFX')

        self.genre = avalon.elms.IdNameElm(
            id=self.genre_id,
            name='Punk')

        self.track1 = avalon.elms.TrackElm(
            id=uuid.uuid4(),
            name="It's My Job To Keep Punk Rock Elite",
            length=80,
            track=1,
            year=1997,
            album='So Long and Thanks for All the Shoes',
            album_id=self.album_id,
            artist='NOFX',
            artist_id=self.artist_id,
            genre='Punk',
            genre_id=self.genre_id)

        self.track2 = avalon.elms.TrackElm(
            id=uuid.uuid4(),
            name="180 Degrees",
            length=130,
            track=5,
            year=1997,
            album='So Long And Thanks For All The Shoes',
            album_id=self.album_id,
            artist='NOFX',
            artist_id=self.artist_id,
            genre='Punk',
            genre_id=self.genre_id)

    def test_search_albums_indexed_under_all_tokens(
            self, album_store, artist_store, genre_store, track_store):
        """Test that an album (and hence all types) are indexed under every
        suffix combination of the name.
        """
        album_store.get_all.return_value = frozenset([self.album])
        artist_store.get_all.return_value = frozenset([self.artist])
        genre_store.get_all.return_value = frozenset([self.genre])
        track_store.get_all.return_value = frozenset([self.track1, self.track2])

        text_search = avalon.web.search.AvalonTextSearch(
            album_store, artist_store, genre_store, track_store, trie_factory)

        text_search.reload()
        assert 1 == len(text_search.search_albums('So Long and Thanks for All the Shoes'))
        assert 1 == len(text_search.search_albums('Long and Thanks for All the Shoes'))
        assert 1 == len(text_search.search_albums('and Thanks for All the Shoes'))
        assert 1 == len(text_search.search_albums('Thanks for All the Shoes'))
        assert 1 == len(text_search.search_albums('for All the Shoes'))
        assert 1 == len(text_search.search_albums('All the Shoes'))
        assert 1 == len(text_search.search_albums('the Shoes'))
        assert 1 == len(text_search.search_albums('Shoes'))

    def test_search_tracks_includes_album_results(
            self, album_store, artist_store, genre_store, track_store):
        """Test that track searches include album results."""
        album_store.get_all.return_value = frozenset([self.album])
        artist_store.get_all.return_value = frozenset([self.artist])
        genre_store.get_all.return_value = frozenset([self.genre])
        track_store.get_all.return_value = frozenset([self.track1, self.track2])
        track_store.get_by_album.side_effect = lambda id: frozenset(
            [self.track1, self.track2]) if id == self.album_id else frozenset()

        text_search = avalon.web.search.AvalonTextSearch(
            album_store, artist_store, genre_store, track_store, trie_factory)

        text_search.reload()
        results = text_search.search_tracks('So Long')
        assert self.track1 in results
        assert self.track2 in results

    def test_search_tracks_includes_artist_results(
            self, album_store, artist_store, genre_store, track_store):
        """Test that track searches include artist results."""
        album_store.get_all.return_value = frozenset([self.album])
        artist_store.get_all.return_value = frozenset([self.artist])
        genre_store.get_all.return_value = frozenset([self.genre])
        track_store.get_all.return_value = frozenset([self.track1, self.track2])
        track_store.get_by_artist.side_effect = lambda id: frozenset(
            [self.track1, self.track2]) if id == self.artist_id else frozenset()

        text_search = avalon.web.search.AvalonTextSearch(
            album_store, artist_store, genre_store, track_store, trie_factory)

        text_search.reload()
        results = text_search.search_tracks('NOFX')
        assert self.track1 in results
        assert self.track2 in results

    def test_search_tracks_includes_genre_results(
            self, album_store, artist_store, genre_store, track_store):
        """Test that track searches include genre results."""
        album_store.get_all.return_value = frozenset([self.album])
        artist_store.get_all.return_value = frozenset([self.artist])
        genre_store.get_all.return_value = frozenset([self.genre])
        track_store.get_all.return_value = frozenset([self.track1, self.track2])
        track_store.get_by_genre.side_effect = lambda id: frozenset(
            [self.track1, self.track2]) if id == self.genre_id else frozenset()

        text_search = avalon.web.search.AvalonTextSearch(
            album_store, artist_store, genre_store, track_store, trie_factory)

        text_search.reload()
        results = text_search.search_tracks('Punk')
        assert self.track1 in results
        assert self.track2 in results

    def test_search_tracks_includes_track_results(
            self, album_store, artist_store, genre_store, track_store):
        """Test that track searches include track name match results."""
        album_store.get_all.return_value = frozenset([self.album])
        artist_store.get_all.return_value = frozenset([self.artist])
        genre_store.get_all.return_value = frozenset([self.genre])
        track_store.get_all.return_value = frozenset([self.track1, self.track2])

        text_search = avalon.web.search.AvalonTextSearch(
            album_store, artist_store, genre_store, track_store, trie_factory)

        text_search.reload()
        assert self.track1 in text_search.search_tracks("It's my job")
        assert self.track2 in text_search.search_tracks('180')
