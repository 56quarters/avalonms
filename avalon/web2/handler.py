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


import functools

import cherrypy

import avalon.err
import avalon.exc
import avalon.web2.filtering
import avalon.web2.api
import avalon.web2.output



__all__ = [
    'application_ready',
    'render_results',
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
            return avalon.web2.output.render(results=func(self, *args, **kwargs))
        except avalon.exc.ApiError, e:
            return avalon.web2.output.render(error=e)
    return wrapper


class AvalonHandlerConfig(object):

    def __init__(self):
        self.api_endpoints = None
        self.status_endpoints = None
        self.filters = []
        self.startup = None


class AvalonHandler(object):
    
    def __init__(self, config):
        """ """
        self._api = config.api_endpoints
        self._status = config.status_endpoints
        self._filters = config.filters
        self._startup = config.startup

    def _filter(self, results, params):
        """ """
        out = list(results)
        for out_filter in self._filters:
            out = out_filter(out, params)
        return out

    @cherrypy.expose
    def index(self, *args, **kwargs):
        return "This is the status"

    @cherrypy.expose
    def heartbeat(self, *args, **kwargs):
        return "OKOKOK"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @render_results
    @application_ready
    def albums(self, *args, **kwargs):
        return self._filter(
            self._api.get_albums(),
            avalon.web2.request.Parameters(kwargs))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @render_results
    @application_ready
    def artists(self, *args, **kwargs):
        return self._filter(
            self._api.get_artists(),
            avalon.web2.request.Parameters(kwargs))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @render_results
    @application_ready
    def genres(self, *args, **kwargs):
        return self._filter(
            self._api.get_genres(),
            avalon.web2.request.Parameters(kwargs))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @render_results
    @application_ready
    def songs(self, *args, **kwargs):
        params = avalon.web2.request.Parameters(kwargs)
        return self._filter(
            self._api.get_songs(params),
            params)

