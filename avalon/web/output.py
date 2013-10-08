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

# TODO: Change output to errors: [], warnings: []

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
