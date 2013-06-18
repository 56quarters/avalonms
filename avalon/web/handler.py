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


"""Avalon web application for handling web requests."""

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
    'AvalonHandler',
    'AvalonHandlerConfig'
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


class AvalonHandlerConfig(object):
    """Configuration for the Avalon web application."""

    def __init__(self):
        self.api_endpoints = None
        self.status_endpoints = None
        self.filters = []
        self.startup = None


class AvalonHandler(object):
    """Avalon web application with status and metadata endpoints."""

    def __init__(self, config):
        """Set the endpoints, filters, and startup time for the handler."""
        self._api = config.api_endpoints
        self._status = config.status_endpoints
        self._filters = config.filters
        self._startup = config.startup

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
        """Application heartbeat endpoint."""
        return self._status.get_heartbeat()

    # NOTE: The text_only keyword argument is required to get the encoding
    # tool to set the ';charset=utf-8' portion of the Content-Type header,
    # otherwise it will only add charset to mime types that begin with text/*.
    # This might not really be needed since JSON requires Unicode and the
    # default is UTF-8 anyway but it shouldn't hurt.

    @cherrypy.expose
    @cherrypy.tools.encode(text_only=False, encoding=avalon.DEFAULT_ENCODING)
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    def server(self, *args, **kwargs):
        """Application status endpoint."""
        return self._status.get_server_data(self._startup, self._api)

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

