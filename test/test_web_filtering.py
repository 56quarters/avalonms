# -*- coding: utf-8 -*-
#

from __future__ import absolute_import, unicode_literals

import collections

import pytest
import avalon.exc
import avalon.web.filtering
import avalon.web.request


class DummyRequest(object):
    def __init__(self, args=None):
        self.args = {} if args is None else args


DummyElm = collections.namedtuple('DummyElm', ['id', 'name'])


class TestSortFilter(object):
    def setup(self):
        elm1 = DummyElm(id=123, name='bcd')
        elm2 = DummyElm(id=456, name='xyz')
        elm3 = DummyElm(id=789, name='abc')

        self.elms = [elm1, elm2, elm3]
        self.asc_sorted = [elm3, elm1, elm2]
        self.desc_sorted = [elm2, elm1, elm3]

    def test_sort_filter_no_field(self):
        """Ensure the elements aren't sorted when no ordering is specified."""
        request = DummyRequest()
        params = avalon.web.request.Parameters(request)
        sorted_elms = avalon.web.filtering.sort_filter(self.elms, params)

        assert sorted_elms == self.elms, "Expected elements the same order"

    def test_sort_filter_invalid_direction(self):
        """Ensure invalid sort directions result in an error."""
        request = DummyRequest({
            'order': 'name',
            'direction': 'foo'})
        params = avalon.web.request.Parameters(request)

        with pytest.raises(avalon.exc.InvalidParameterValueError):
            avalon.web.filtering.sort_filter(self.elms, params)

    def test_sort_filter_invalid_field(self):
        """Ensure invalid sort fields result in an error."""
        request = DummyRequest({'order': 'foo'})
        params = avalon.web.request.Parameters(request)

        with pytest.raises(avalon.exc.InvalidParameterNameError):
            avalon.web.filtering.sort_filter(self.elms, params)

    def test_sort_filter_normal_direction(self):
        """Ensure we can sort elements in ascending order."""
        request = DummyRequest({
            'order': 'name',
            'direction': 'asc'})
        params = avalon.web.request.Parameters(request)
        sorted_elms = avalon.web.filtering.sort_filter(self.elms, params)
        assert sorted_elms == self.asc_sorted, "Did not get ASC sorted elms"

    def test_sort_filter_reverse_direction(self):
        """Ensure we can sort elements in descending order."""
        request = DummyRequest({
            'order': 'name',
            'direction': 'desc'})
        params = avalon.web.request.Parameters(request)
        sorted_elms = avalon.web.filtering.sort_filter(self.elms, params)
        assert sorted_elms == self.desc_sorted, "Did not get DESC sorted elms"


class TestLimitFilter(object):
    def setup(self):
        elm1 = DummyElm(id=123, name='bcd')
        elm2 = DummyElm(id=456, name='xyz')
        elm3 = DummyElm(id=789, name='abc')
        self.elms = [elm1, elm2, elm3]

    def test_limit_filter_no_limit(self):
        """Ensure all results are return when not limited."""
        request = DummyRequest()
        params = avalon.web.request.Parameters(request)
        limited = avalon.web.filtering.limit_filter(self.elms, params)

        assert 3 == len(limited), "Did not get expected number of results"
        assert limited == self.elms, "Did not get expected results"

    def test_limit_filter_negative_limit(self):
        """Ensure negative limits are treated as invalid."""
        request = DummyRequest({
            'limit': '-1'})
        params = avalon.web.request.Parameters(request)

        with pytest.raises(avalon.exc.InvalidParameterValueError):
            avalon.web.filtering.limit_filter(self.elms, params)

    def test_limit_filter_negative_offset(self):
        """Ensure negative offsets are treated as invalid."""
        request = DummyRequest({
            'limit': '1',
            'offset': '-1'})
        params = avalon.web.request.Parameters(request)

        with pytest.raises(avalon.exc.InvalidParameterValueError):
            avalon.web.filtering.limit_filter(self.elms, params)

    def test_limit_filter_success(self):
        """Ensure we can apply limits and offsets to results."""
        request = DummyRequest({
            'limit': '1',
            'offset': '1'})
        params = avalon.web.request.Parameters(request)
        limited = avalon.web.filtering.limit_filter(self.elms, params)

        assert 1 == len(limited), "Did not get expected result size"
        assert self.elms[1] == limited[0], "Did not get expected result"
