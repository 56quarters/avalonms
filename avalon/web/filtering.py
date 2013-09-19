# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2013 TSH Labs <projects@tshlabs.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""Callbacks for sorting and limiting result sets."""

import avalon.err
import avalon.exc


__all__ = [
    'SORT_ASC',
    'SORT_DESC',
    'limit_filter',
    'sort_filter'
]


class _SortHelper(object):
    """Object meant to be used as a comparison function
    for objects based on their attributes.

    Doing sorting this way allows more flexibility than
    implementing the __cmp__ method for each object since
    that limits sorting to a single field.
    """

    def __init__(self, field):
        """Set the field to be used for sorting."""
        self.field = field

    def __call__(self, obj1, obj2):
        """Return the results of cmp() on the field of
        the two given objects.

        NOTE: We're not handling any potential AttributeError
        exceptions here on purpose since we want the caller to
        handle that as an invalid field.
        """
        val1 = getattr(obj1, self.field)
        val2 = getattr(obj2, self.field)
        return cmp(val1, val2)


SORT_DESC = 'desc'
SORT_ASC = 'asc'


def sort_filter(elms, params):
    """Use query string parameters to sort the result set appropriately
    based on the value of the 'order' and 'direction' parameters and return
    the sorted list of elements.

    Both are optional, however invalid values for either will result in
    an :class:`InvalidParameterException` being raised.
    """
    field = params.get('order')
    direction = params.get('direction', 'asc')
    sort_helper = _SortHelper(field)

    if field is None:
        return elms

    if direction not in (SORT_ASC, SORT_DESC):
        raise avalon.exc.InvalidParameterError(
            avalon.err.ERROR_INVALID_FIELD_VALUE('direction'))

    reverse = SORT_DESC == direction

    try:
        elms.sort(cmp=sort_helper, reverse=reverse)
    except AttributeError:
        raise avalon.exc.InvalidParameterError(
            avalon.err.ERROR_INVALID_FIELD_VALUE('order'))
    return elms


def limit_filter(elms, params):
    """Use query string parameters to only return a portion of the result
    set based on the value of the'limit' and 'order' parameters.

    Both are optional, however invalid values for either will results in
    an :class:`InvalidParameterException` being raised.
    """
    limit = params.get_int('limit')
    offset = params.get_int('offset', 0)

    if limit is None:
        return elms

    if limit < 0:
        raise avalon.exc.InvalidParameterError(
            avalon.err.ERROR_NEGATIVE_FIELD_VALUE('limit'))
    if offset < 0:
        raise avalon.exc.InvalidParameterError(
            avalon.err.ERROR_NEGATIVE_FIELD_VALUE('offset'))

    start = offset
    end = offset + limit
    return elms[start:end]

