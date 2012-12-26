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


"""Avalon web application for handling requests."""


import functools

import cherrypy

import avalon.err
import avalon.exc
import avalon.web.api
import avalon.web.filtering
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
    def index(self, *args, **kwargs):
        """Application status page."""
        return self._status.get_status_page(self._startup, self._api)

    @cherrypy.expose
    def heartbeat(self, *args, **kwargs):
        """Application heartbeat endpoint."""
        return self._status.get_heartbeat()

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    @render_results
    @application_ready
    @convert_parameters
    def albums(self, params):
        """Albums metadata endpoint."""
        return self._filter(self._api.get_albums(params), params)

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    @render_results
    @application_ready
    @convert_parameters
    def artists(self, params):
        """Artists metadata endpoint."""
        return self._filter(self._api.get_artists(params), params)

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    @render_results
    @application_ready
    @convert_parameters
    def genres(self, params):
        """Genres metadata endpoint."""
        return self._filter(self._api.get_genres(params), params)

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=avalon.web.output.json_handler)
    @render_results
    @application_ready
    @convert_parameters
    def songs(self, params):
        """Songs metadata endpoint."""
        return self._filter(self._api.get_songs(params), params)

