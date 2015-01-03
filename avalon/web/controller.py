# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Avalon web application for handling web requests.

The :class:`AvalonController` class acts as the main interface between the
web server and the rest of the application.
"""

from __future__ import absolute_import, unicode_literals
import functools

from flask import request
import avalon
import avalon.exc
import avalon.log
import avalon.metrics
import avalon.web.response
import avalon.web.request


__all__ = [
    'render_results',
    'convert_parameters',
    'AvalonController',
    'AvalonControllerConfig'
]


def render_results(func):
    """Decorator to convert the results of a function into a dictionary
    and then "jsonify" it to be rendered by Flask.

    Any :class:`avalon.exc.ApiError` errors raised will be caught and used
    to render an error response. We do this because these are not really
    exceptional errors and don't merit any special logging or events being
    published (ala Flask signals).
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return avalon.web.response.render(results=func(self, *args, **kwargs))
        except avalon.exc.ApiError as e:
            return avalon.web.response.render(error=e), e.http_code

    return wrapper


def convert_parameters(func):
    """Decorator to convert Flask request.args into an Avalon
     :class:`avalon.web.request.Parameters` instance to allow
     query string parameters to be retrieved with specific types.
     """

    @functools.wraps(func)
    def wrapper(self):
        return func(self, avalon.web.request.Parameters(request))

    return wrapper


class AvalonControllerConfig(object):
    """Configuration for the Avalon web application."""

    def __init__(self):
        self.api_endpoints = None
        self.filters = []


class AvalonController(object):
    """Avalon web application with web-exposed metadata endpoints."""

    _logger = avalon.log.get_error_log()

    def __init__(self, config):
        """Set the endpoints and filters for the controller."""
        self._api = config.api_endpoints
        self._filters = config.filters

    def _filter(self, results, params):
        """Apply each of the filter callbacks to the results."""
        out = list(results)
        for out_filter in self._filters:
            out = out_filter(out, params)
        return out

    def reload(self):
        """Reload any cache values for the API and status handlers."""
        self._api.reload()

    def get_heartbeat(self):
        """Return the string 'OKOKOK' if start up is complete.

        Note that there is no real logic behind this, it only acts as a known
        value that a deploy script or load balancer could check for to ensure
        the application has finished starting.
        """
        return 'OKOKOK'

    def get_version(self):
        """Return the version of the currently running server."""
        return avalon.__version__

    @avalon.metrics.timed('request.albums')
    @render_results
    @convert_parameters
    def get_albums(self, params):
        """Albums metadata endpoint."""
        return self._filter(self._api.get_albums(params), params)

    @avalon.metrics.timed('request.artists')
    @render_results
    @convert_parameters
    def get_artists(self, params):
        """Artists metadata endpoint."""
        return self._filter(self._api.get_artists(params), params)

    @avalon.metrics.timed('request.genres')
    @render_results
    @convert_parameters
    def get_genres(self, params):
        """Genres metadata endpoint."""
        return self._filter(self._api.get_genres(params), params)

    @avalon.metrics.timed('request.songs')
    @render_results
    @convert_parameters
    def get_songs(self, params):
        """Songs metadata endpoint."""
        return self._filter(self._api.get_songs(params), params)

    def handle_unknown_error(self, e):
        """Handle an unexpected :class:`Exception` raised during a request
        by logging it, rendering an error and returning and HTTP 500 status
        code.

        :param Exception e: Unexpected error raised during the course of
            handling a service request
        :return: Formatted JSON response representing the error
        :rtype: flask.Response
        """
        self._logger.exception(
            'Unhandled exception processing %s: %s', request.url, e)

        err = avalon.exc.ServiceUnknownError('%s' % e)
        return avalon.web.response.render(error=err), err.http_code
