# -*- coding: utf-8 -*-
#

import avalon.web.search


class TestSearchable(object):
    def test_searchable_no_input(self):
        assert '' == avalon.web.search.searchable(None)

    def test_searchable_umlaut_mixed_case(self):
        word = u'Düsseldorf'
        assert 'dusseldorf' == avalon.web.search.searchable(word)

    def test_searchable_accent_mixed_case(self):
        word = u'Verás'
        assert 'veras' == avalon.web.search.searchable(word)


class TestStripAccents(object):
    def test_strip_accents_umlaut(self):
        word = u'Düsseldorf'
        assert 'Dusseldorf' == avalon.web.search.strip_accents(word)

    def test_strip_accents_accent(self):
        word = u'Verás'
        assert 'Veras' == avalon.web.search.strip_accents(word)


class TestTrieNode(object):
    def test_elements_empty(self):
        node = avalon.web.search.TrieNode()
        assert 0 == len(node.get_elements())

    def test_one_element(self):
        node = avalon.web.search.TrieNode()
        node.add_element(123)

        elms = node.get_elements()
        assert 1 == len(elms)
        assert 123 in elms

    def test_two_elements(self):
        node = avalon.web.search.TrieNode()
        node.add_element(123)
        node.add_element(456)

        elms = node.get_elements()
        assert 2 == len(elms)
        assert 123 in elms
        assert 456 in elms

    def test_children_empty(self):
        node = avalon.web.search.TrieNode()
        assert 0 == len(node.get_children())

    def test_one_child(self):
        node = avalon.web.search.TrieNode()
        child = avalon.web.search.TrieNode()

        node.add_child('a', child)
        children = node.get_children()
        assert 1 == len(children)
        assert 'a' in children

    def test_two_children(self):
        node = avalon.web.search.TrieNode()
        child1 = avalon.web.search.TrieNode()
        child2 = avalon.web.search.TrieNode()

        node.add_child('a', child1)
        node.add_child('b', child2)
        children = node.get_children()
        assert 2 == len(children)
        assert 'a' in children
        assert 'b' in children


class TestSearchTrie(object):
    pass


class TestAvalonTextSearch(object):
    pass
