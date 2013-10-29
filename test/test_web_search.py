# -*- coding: utf-8 -*-
#

import avalon.web.search


class TestSearchable(object):
    def test_searchable_no_input(self):
        """Ensure that None input is handle reasonably."""
        assert '' == avalon.web.search.searchable(None)

    def test_searchable_umlaut_mixed_case(self):
        """Ensure that umlauts are removed and case is converted."""
        word = u'Düsseldorf'
        assert 'dusseldorf' == avalon.web.search.searchable(word)

    def test_searchable_accent_mixed_case(self):
        """Ensure that accents are removed and case is converted."""
        word = u'Verás'
        assert 'veras' == avalon.web.search.searchable(word)


class TestStripAccents(object):
    def test_strip_accents_umlaut(self):
        """Ensure that umlauts are removed and case is preserved."""
        word = u'Düsseldorf'
        assert 'Dusseldorf' == avalon.web.search.strip_accents(word)

    def test_strip_accents_accent(self):
        """Ensure that accents are removed and case is preserved."""
        word = u'Verás'
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


def _node_factory():
    return avalon.web.search.TrieNode()

class TestSearchTrie(object):

    def test_init_creates_root(self):
        """Ensure that the initial construction of the trie creates
        a root node and that the size of this empty trie is 1.
        """
        trie = avalon.web.search.SearchTrie(_node_factory)
        assert trie._root is not None
        assert trie._size == 1

    def test_add_creates_initial_nodes(self):
        """Ensure that adding a single term to the trie builds additional
        nodes off of the root node and that they are indexed as expected.
        """
        trie = avalon.web.search.SearchTrie(_node_factory)
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
        trie = avalon.web.search.SearchTrie(_node_factory)
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


class TestAvalonTextSearch(object):
    pass
