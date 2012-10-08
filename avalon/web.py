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


"""Application frontend for handling requests."""


import collections
import functools
import simplejson
import threading
import uuid
from datetime import datetime

import cherrypy

import avalon.err
import avalon.exc
import avalon.services
import avalon.elms


__all__ = [
    'AvalonHandler'
    ]


_STATUS_PAGE_TPT = """<!DOCTYPE html>
<html>
<head>
  <title>Avalon Music Server</title>
  <style type="text/css">
    body {
      background-color: #363636;
      color: #E7E7E7;
      font-family: helvetica, arial, sans-serif;
      font-size: 14px;
      line-height: 20px;
    }
    h1 {
      border-bottom: 1px solid #FFF;
      color: #00ADEE;
      margin-top: 10px;
      padding-bottom: 15px;
      text-shadow: 0 0 1px #444;
    }
    dt {
      color: #00ADEE;
      font-weight: bold;
      margin-top: 10px;
    }
    .stats {
      background-color: #171717;
      border: 1px solid #FFF;
      border-radius: 15px;
      box-shadow: 0 3px 3px 3px #444;
      margin: 50px auto;
      padding: 15px;
      width: 500px;
    }
    .not_ready {
      color: #C00;
      font-weight: bold;
     }
  </style>
</head>
<body>
  <div class="stats">
  <h1>Avalon Music Server</h1>
  <dl>
    <dt>Server is:</dt>
    <dd class="%(class)s">%(status)s</dd>

    <dt>Running as:</dt>
    <dd>%(user)s:%(group)s</dd>

    <dt>Uptime:</dt>
    <dd>%(uptime)s</dd>

    <dt>Memory:</dt>
    <dd>%(memory)s MB</dd>

    <dt>Threads:</dt>
    <dd>%(threads)s</dd>

    <dt>Loaded:</dt>
    <dd>
      Albums: %(albums)s<br /> 
      Artists: %(artists)s<br /> 
      Genres: %(genres)s<br /> 
      Tracks: %(tracks)s<br />
    </dd>
  </dl>
  </div>
</body>
</html>
"""


class _AvalonJSONHandler(object):

    """CherryPy compatible JSON encoder wrapper."""

    def __init__(self, encoder=None):
        if encoder is None:
            encoder = _OurEncoder()
        self._encoder = encoder

    def __call__(self, *args, **kwargs):
        value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
        return self._encoder.encode(value)


class _OurEncoder(simplejson.JSONEncoder):
    
    """JSON encoder that knows how to deal with UUID objects."""
    
    def default(self, o):
        """Encode UUID objects or delegate to the parent class."""
        if isinstance(o, uuid.UUID):
            return str(o)
        return super(_OurEncoder, self).default(o)


def _application_ready(func):
    """Decorator for checking if the application has started."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.ready:
            raise avalon.exc.ServerNotReadyError(
                avalon.err.ERROR_SERVER_NOT_READY())
        return func(self, *args, **kwargs)
    return wrapper


def _render_results(func):
    """Render the results of method calls and any ApiErrors raised 
    by the method as output."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return _get_output(res=func(self, *args, **kwargs))
        except avalon.exc.ApiError, e:
            return _get_output(err=e)
    return wrapper


class AvalonHandler(object):

    """Handle HTTP requests and return result sets in JSON."""

    def __init__(self, session_handler):
        """Initialize each of the stores by loading from the database."""
        self._tracks = avalon.services.TrackStore(session_handler)
        self._albums = avalon.services.AlbumStore(session_handler)
        self._artists = avalon.services.ArtistStore(session_handler)
        self._genres = avalon.services.GenreStore(session_handler)
        self._id_cache = avalon.services.IdLookupCache(session_handler)
        self._startup = datetime.utcnow()
        self._ready = threading.Event()

    def _get_ready(self):
        """Get the status of the server."""
        return self._ready.is_set()

    def _set_ready(self, val):
        """Set the status of the server."""
        if val:
            self._ready.set()
        else:
            self._ready.clear()

    ready = property(
        _get_ready, _set_ready, None, 
        "Is the application ready to handle requests")

    def reload(self):
        """Reload in memory stores from the database."""
        self._tracks.reload()
        self._albums.reload()
        self._artists.reload()
        self._genres.reload()
        self._id_cache.reload()

    @cherrypy.expose
    def index(self, *args, **kwargs):
        """Display a server status page."""
        status = 'READY'
        css = ''
        if not self.ready:
            status = 'NOT READY'
            css = 'not_ready'

        return _STATUS_PAGE_TPT % {
            'status': status,
            'class': css,
            'user': avalon.util.get_current_uname(),
            'group': avalon.util.get_current_gname(),
            'uptime': datetime.utcnow() - self._startup,
            'memory': avalon.util.get_mem_usage(),
            'threads': '<br />'.join(avalon.util.get_thread_names()),
            'albums': len(self._albums.all()),
            'artists': len(self._artists.all()),
            'genres': len(self._genres.all()),
            'tracks': len(self._tracks.all())
            }

    @cherrypy.expose
    def heartbeat(self, *args, **kwargs):
        """Display the string 'OKOKOK' if the server is
        ready to handle requests, 'NONONO' otherwise.
        """
        if self.ready:
            return "OKOKOK"
        _set_http_status(503)
        return "NONONO"

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=_AvalonJSONHandler())
    @_render_results
    @_application_ready
    def albums(self, *args, **kwargs):
        """Return a list of all albums."""
        return _filter(self._albums.all(), _RequestParams(kwargs))

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=_AvalonJSONHandler())
    @_render_results
    @_application_ready
    def artists(self, *args, **kwargs):
        """Return a list of all artists."""
        return _filter(self._artists.all(), _RequestParams(kwargs))

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=_AvalonJSONHandler())
    @_render_results
    @_application_ready
    def genres(self, *args, **kwargs):
        """Return a list of all genres."""
        return _filter(self._genres.all(), _RequestParams(kwargs))

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=_AvalonJSONHandler())
    @_render_results
    @_application_ready
    def songs(self, *args, **kwargs):
        """Return song results based on the given query string parameters."""
        params = _RequestParams(kwargs)
        sets = []

        if None is not params.get('album'):
            sets.append(
                self._tracks.by_album(
                    self._id_cache.get_album_id(params.get('album'))))
        if None is not params.get('artist'):
            sets.append(
                self._tracks.by_artist(
                    self._id_cache.get_artist_id(params.get('artist'))))
        if None is not params.get('genre'):
            sets.append(
                self._tracks.by_genre(
                    self._id_cache.get_genre_id(params.get('genre'))))

        if None is not params.get('album_id'):
            sets.append(self._tracks.by_album(params.get('album_id')))
        if None is not params.get('artist_id'):
            sets.append(self._tracks.by_artist(params.get('artist_id')))
        if None is not params.get('genre_id'):
            sets.append(self._tracks.by_genre(params.get('genre_id')))
            
        if sets:
            # Return the intersection of any non-None sets
            return _filter(_reduce(sets), params)
        # There were no parameters to filter songs by any criteria
        return _filter(self._tracks.all(), params)


def _set_http_status(code):
    """Set the HTTP status of the current response."""
    cherrypy.serving.response.status = code


def _filter(results, params):
    """Apply any limits, offsets, or ordering to the results."""
    out = list(results)
    for callback in (_apply_sort, _apply_limit):
        out = callback(out, params)
    return out


def _reduce(sets):
    """Find the intersection of all of the given non-None sets."""
    # NOTE: we use 'not None' here instead of a simple boolean test
    # because we want the intersection with an empty set to actually
    # mean 'there were 0 results'.
    return functools.reduce(
        lambda x, y: x.intersection(y),
        [res_set for res_set in sets if res_set is not None])


class _RequestOutput(object):

    """Render query results or errors in a format that can be serialized
    to JSON.
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

    def _set_error_status(self):
        """Set and HTTP status for the current request if this error
        has one that makes sense.
        """
        if self.error is None:
            return

        code = self.error.http_code
        if code != 0:
            # Set the status of the currently processing request
            # while still allowing us to render our JSON payload
            # with further information about the error
            _set_http_status(code)

    def render(self):
        """Format any results or errors as a dictionary to be turned into a
        JSON payload.
        """
        err = self._format_error()
        res = self._format_results()
        self._set_error_status()

        return {
            'is_error': err['is_error'],
            'error_name': err['error_name'],
            'error_msg': err['error_msg'],
            'result_count': res['result_count'],
            'results': res['results']
            }


def _get_output(res=None, err=None):
    """Render results or an error as an iterable."""
    out = _RequestOutput()
    if res is not None:
        out.results = res
    if err is not None:
        out.error = err
    return out.render()


class _RequestParams(object):

    """Logic for accessing query string parameters of interest."""

    valid = frozenset(['album', 'album_id', 'artist', 'artist_id', 
                        'direction', 'order', 'genre', 'genre_id',
                        'limit', 'offset'])

    def __init__(self, qs):
        """Set the query string params to use."""
        self._qs = qs

    def get_int(self, field, default=None):
        """Return the value of the field as an int, raising an error if
        it isn't a valid field or cannot be converted to an int, and
        returning None if the field isn't in the query string.
        """
        val = self.get(field)
        if val is None:
            return default

        try:
            return int(val)
        except ValueError:
            raise avalon.exc.InvalidParameterError(
                avalon.err.ERROR_INVALID_FIELD_VALUE(field))

    def get(self, field, default=None):
        """Return the value of the field, raising an error if it isn't
        a valid field, and returning None if the field isn't in the query
        string.
        """
        if field not in self.valid:
            raise avalon.exc.InvalidParameterError(
                avalon.err.ERROR_INVALID_FIELD(field))
        
        if field not in self._qs:
            return default
        return self._qs[field]


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


def _apply_sort(elms, params):
    """Return a sorted list from the given elements and query
    string parameters
    """
    field = params.get('order')
    direction = params.get('direction', 'asc')
    
    if field is None:
        return elms    
    if direction not in ('asc', 'desc'):
        raise avalon.exc.InvalidParameterError(
            avalon.err.ERROR_INVALID_FIELD_VALUE('direction'))
        
    reverse = 'desc' == direction
    helper = _SortHelper(field)
    
    try:
        elms.sort(cmp=helper, reverse=reverse)
    except AttributeError:
        raise avalon.exc.InvalidParameterError(
            avalon.err.ERROR_INVALID_FIELD_VALUE('order'))
    return elms

    
def _apply_limit(elms, params):
    """Return a limited list from the given elements and query
    string parameters
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

