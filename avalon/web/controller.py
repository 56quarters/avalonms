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


"""Avalon web application for handling web requests.

The :class:`AvalonHandler` class acts as the main interface between the
web server and the rest of the application.
"""

import functools

import cherrypy

import avalon
import avalon.err
import avalon.exc
import avalon.web.output
import avalon.web.request


__all__ = [
    'application_ready',
    'render_results',
    'convert_parameters',
    'AvalonController',
    'AvalonControllerConfig'
]


def application_ready(func):
    """Decorator for checking if the application has started."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.ready:
            raise avalon.exc.ServerNotReadyError(
                avalon.err.ERROR_SERVER_NOT_READY())
        return func(self, *args, **kwargs)
    return wrapper


def render_results(func):
    """Decorator to render the results of method calls and 
    any ApiErrors raised by the method as output that can be
    correctly serialized by simplejson.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return avalon.web.output.render(results=func(self, *args, **kwargs))
        except avalon.exc.ApiError, e:
            avalon.web.output.set_http_status(e.http_code)
            return avalon.web.output.render(error=e)
    return wrapper


def convert_parameters(func):
    """Decorator to convert the standard cherrypy *args and **kwargs
    method arguments into our Parameters object to pass to the method.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, avalon.web.request.Parameters(kwargs))
    return wrapper


class AvalonControllerConfig(object):
    """Configuration for the Avalon web application."""

    def __init__(self):
        self.api_endpoints = None
        self.status_endpoints = None
        self.filters = []


class AvalonController(object):
    """Avalon web application with status and metadata endpoints."""

    def __init__(self, config):
        """Set the endpoints and filters for the controller."""
        self._api = config.api_endpoints
        self._status = config.status_endpoints
        self._filters = config.filters

    def _filter(self, results, params):
        """Apply each of the filter callbacks to the results."""
        out = list(results)
        for out_filter in self._filters:
            out = out_filter(out, params)
        return out

    def _get_ready(self):
        """Get the ready state of the application."""
        return self._status.ready

    def _set_ready(self, val):
        """Set the ready state of the application."""
        self._status.ready = val

    ready = property(
        _get_ready, _set_ready, None, "Is the application ready")

    def reload(self):
        """Reload any cache values for the API and status handlers."""
        self._api.reload()
        self._status.reload()

    @cherrypy.expose
    def heartbeat(self, *args, **kwargs):
        """Return the string 'OKOKOK' if start up is complete, 'NONONO' otherwise."""
        return self._status.get_heartbeat()

    @cherrypy.expose
    def uptime(self, *args, **kwargs):
        """Return the number of seconds since server start up."""
        return str(self._status.get_uptime().seconds)

    @cherrypy.expose
    def memory(self, *args, **kwargs):
        """Return the amount of memory used in megabytes."""
        return "%.2f" % self._status.get_memory_usage()

    @cherrypy.expose
    @cherrypy.tools.encode(text_only=False, encoding=avalon.DEFAULT_ENCODING)
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    def threads(self, *args, **kwargs):
        """Return a list of thread names as JSON."""
        return self._status.get_threads()

    # NOTE: The text_only keyword argument is required to get the encoding
    # tool to set the ';charset=utf-8' portion of the Content-Type header,
    # otherwise it will only add charset to mime types that begin with text/*.
    # This might not really be needed since JSON requires Unicode and the
    # default is UTF-8 anyway but it shouldn't hurt.

    @cherrypy.expose
    @cherrypy.tools.encode(text_only=False, encoding=avalon.DEFAULT_ENCODING)
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    @render_results
    @application_ready
    @convert_parameters
    def albums(self, params):
        """Albums metadata endpoint."""
        return self._filter(self._api.get_albums(params), params)

    @cherrypy.expose
    @cherrypy.tools.encode(text_only=False, encoding=avalon.DEFAULT_ENCODING)
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    @render_results
    @application_ready
    @convert_parameters
    def artists(self, params):
        """Artists metadata endpoint."""
        return self._filter(self._api.get_artists(params), params)

    @cherrypy.expose
    @cherrypy.tools.encode(text_only=False, encoding=avalon.DEFAULT_ENCODING)
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    @render_results
    @application_ready
    @convert_parameters
    def genres(self, params):
        """Genres metadata endpoint."""
        return self._filter(self._api.get_genres(params), params)

    @cherrypy.expose
    @cherrypy.tools.encode(text_only=False, encoding=avalon.DEFAULT_ENCODING)
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    @render_results
    @application_ready
    @convert_parameters
    def songs(self, params):
        """Songs metadata endpoint."""
        return self._filter(self._api.get_songs(params), params)

