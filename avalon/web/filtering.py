# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Callbacks for sorting and limiting result sets."""

from __future__ import absolute_import, unicode_literals
import avalon.exc


__all__ = [
    'SORT_ASC',
    'SORT_DESC',
    'limit_filter',
    'sort_filter'
]

SORT_DESC = 'desc'
SORT_ASC = 'asc'


def sort_filter(elms, params):
    """Use query string parameters to sort the result set appropriately
    based on the value of the 'order' and 'direction' parameters and return
    the sorted list of elements.

    Both are optional, however invalid values for either will result in
    exceptions being raised.

    :param list elms: Elements to sort
    :param avalon.request.Parameters params: Caller request parameters
    :return: Elements sorted by requested parameters
    :rtype: list
    :raises avalon.exc.InvalidParameterValueError: If sort direction is
        present and invalid
    :raises avalon.exc.InvalidParameterNameError: If order is present and
        does not correspond to a field in the results
    """
    field = params.get('order')
    direction = params.get('direction', SORT_ASC)

    if field is None:
        return elms

    if direction not in (SORT_ASC, SORT_DESC):
        raise avalon.exc.InvalidParameterValueError(
            "Invalid sort direction '{direction}'",
            direction=direction)

    sort_key = lambda elm: getattr(elm, field)
    reverse = SORT_DESC == direction

    try:
        elms.sort(key=sort_key, reverse=reverse)
    except AttributeError:
        raise avalon.exc.InvalidParameterNameError(
            "Invalid order-by field '{field}'", field=field)
    return elms


def limit_filter(elms, params):
    """Use query string parameters to only return a portion of the result
    set based on the value of the 'limit' and 'order' parameters.

    Both are optional, however invalid values for either will result in
    exceptions being raised.

    :param list elms: Elements to limit
    :param avalon.request.Parameters params: Caller request parameters
    :return: Limited and offset results
    :rtype: list
    :raises avalon.exc.InvalidParameterValueError: If either limit or offset
        is present and not an integer or negative
    """
    limit = params.get_int('limit')
    offset = params.get_int('offset', 0)

    if limit is None:
        return elms

    if limit < 0:
        raise avalon.exc.InvalidParameterValueError(
            "The value of limit may not be negative",
            field='limit', value=limit)
    if offset < 0:
        raise avalon.exc.InvalidParameterValueError(
            "The value of offset may not be negative",
            field='offset', value=offset)

    start = offset
    end = offset + limit
    return elms[start:end]
