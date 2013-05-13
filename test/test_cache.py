# -*- coding: utf-8 -*-
#

import pytest

import avalon.cache


class TestFunctions(object):
    def test_get_frozen_mapping(self):
        mapping = {'foo': set(['zing', 'zam', 'zowey'])}
        frozen = avalon.cache.get_frozen_mapping(mapping)

        assert 'foo' in frozen
        assert frozen['foo'] == frozenset(['zing', 'zam', 'zowey'])
        assert isinstance(frozen['foo'], frozenset)

        with pytest.raises(AttributeError):
            frozen['foo'].add('blah')


class TestIdLookupCache(object):
    pass
