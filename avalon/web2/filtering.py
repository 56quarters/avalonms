# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright (c) 2012 TSH Labs <projects@tshlabs.org>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


""" """


import functools
import threading
from datetime import datetime

import cherrypy

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
        
    def __call__(self, o1, o2):
        """Return the results of cmp() on the field of
        the two given objects.
        """
        v1 = getattr(o1, self.field)
        v2 = getattr(o2, self.field)
        return cmp(v1, v2)


SORT_DESC = 'desc'
SORT_ASC = 'asc'


def sort_filter(elms, params):
    """ """
    field = params.get('order')
    direction = params.get('direction', 'asc')
    sort_helper = SortHelper(field)

    if field is None:
        return elms    

    if direction not in (sort_asc, sort_desc):
        raise avalon.exc.InvalidParameterError(
            avalon.err.ERROR_INVALID_FIELD_VALUE('direction'))
        
    reverse = sort_desc == direction
    
    try:
        elms.sort(cmp=sort_helper, reverse=reverse)
    except AttributeError:
        raise avalon.exc.InvalidParameterError(
            avalon.err.ERROR_INVALID_FIELD_VALUE('order'))
    return elms


def limit_filter(elms, params):
    """ """
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

