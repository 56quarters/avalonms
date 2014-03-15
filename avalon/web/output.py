# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


"""Methods for converting results or errors to a serializable format
and rendering them as JSON.
"""

import uuid

import cherrypy
# NOTE: We use simplejson explicitly here instead of the stdlib
# json module since simplejson renders named tuples as JSON
# objects and the stdlib json renders them as JSON lists.
import simplejson


__all__ = [
    'json_handler',
    'render',
    'set_http_status',
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
            out['error_name'] = self.error.error_name
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


def set_http_status(code):
    """Set the given HTTP status code for the reponse currently
    being served.
    """
    cherrypy.response.status = code
