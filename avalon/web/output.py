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


"""Methods for converting results or errors to a serializable format
and then rendering them as JSON.
"""


import uuid

import cherrypy
import simplejson


__all__ = [
    'json_handler',
    'render',
    'JsonEncoder',
    'JsonHandler',
    'RequestOutput'
    ]


class JsonHandler(object):

    """Adapter to use our own JSON encoder with CherryPy."""

    def __init__(self, encoder):
        """Set the JSON encoder to use."""
        self._encoder = encoder

    def __call__(self, *args, **kwargs):
        """Encode the output from a request as JSON."""
        value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
        return self._encoder.encode(value)


class JsonEncoder(simplejson.JSONEncoder):

    """Avalon specific JSON encoder."""

    def default(self, o):
        """Handle encoding a UUID to JSON."""
        if isinstance(o, uuid.UUID):
            return str(o)
        return super(JsonEncoder, self).default(o)


# Singleton instance of a handler callable
json_handler = JsonHandler(JsonEncoder())


def render(results=None, error=None):
    """Factory function for a RequestOutput object with optional
    error and success payload parameters.
    """
    output = RequestOutput()
    if results is not None:
        output.results = results
    if error is not None:
        output.error = error
    return output.render()


class RequestOutput(object):

    """Format results or errors encountered using builtin
    structures and types (mostly).
    """

    def __init__(self):
        """Initialize errors and results from this query."""
        self.error = None
        self.results = []

    def _format_error(self):
        """Format a query error (if there was one)."""
        out = {
            'is_error': False,
            'error_name': '',
            'error_msg': ''
            }
        if self.error is not None:
            out['is_error'] = True
            out['error_name'] = self.error.name
            out['error_msg'] = self.error.message
        return out
        
    def _format_results(self):
        """Format query results (if any)."""
        out = {
            'result_count': 0,
            'results': []
            }
        
        if self.results is not None:
            out['result_count'] = len(self.results)
            out['results'] = self.results
        return out

    def render(self):
        """Format any results or errors as a dictionary to be turned into a
        JSON payload.
        """
        err = self._format_error()
        res = self._format_results()

        return {
            'is_error': err['is_error'],
            'error_name': err['error_name'],
            'error_msg': err['error_msg'],
            'result_count': res['result_count'],
            'results': res['results']
            }

