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
    def test_add_one_element(self):
        pass

    def test_add_two_elements(self):
        pass

    def test_get_elements_empty(self):
        pass

    def test_get_elements_one_element(self):
        pass

    def test_get_elements_two_elements(self):
        pass


class TestSearchTrie(object):
    pass


class TestAvalonTextSearch(object):
    pass
