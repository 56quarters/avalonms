# -*- coding: utf-8 -*-
#


import avalon.web.services


def test_intersection_with_empty_set():
    set1 = set(['foo', 'bar'])
    set2 = set(['foo'])
    set3 = set()

    res = avalon.web.services.intersection([set1, set2, set3])
    assert 0 == len(res), 'Expected empty set of common results'


def test_intersection_no_overlap():
    set1 = set(['foo', 'bar'])
    set2 = set(['baz'])
    set3 = set(['bing'])

    res = avalon.web.services.intersection([set1, set2, set3])
    assert 0 == len(res), 'Expected empty set of common results'


def test_intersection_with_overlap():
    set1 = set(['foo', 'bar'])
    set2 = set(['foo', 'baz'])
    set3 = set(['bing', 'foo'])

    res = avalon.web.services.intersection([set1, set2, set3])
    assert 1 == len(res), 'Expected set of one common result'
