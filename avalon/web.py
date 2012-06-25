# -*- coding: utf-8 -*-
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


import functools
import logging
import threading
import traceback
from datetime import datetime

import cherrypy

import avalon.err
import avalon.exc
import avalon.services
import avalon.elms


__all__ = [
    'set_http_status',
    'AvalonHandler',
    'JSONOutHandler',
    'RequestOutput',
    'RequestParams'
    ]


def set_http_status(code):
    """Set the HTTP status of the current response."""
    cherrypy.serving.response.status = code


class JSONOutHandler(object):

    """Wrap our JSON encoder for objects in the views module
    such that it can be called by the cherrypy JSON output tool.
    """

    def __init__(self):
        """Create an instance of our custom encoder."""
        self._encoder = avalon.elms.JSONEncoder()

    def __call__(self, *args, **kwargs):
        """Return the rendered content encoded as JSON."""
        value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
        return self._encoder.encode(value)



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


def application_ready(func):
    """Decorator for checking if the application has started."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.ready:
           raise avalon.exc.ServerNotReadyError(
                avalon.err.ERROR_SERVER_NOT_READY())
        return func(self, *args, **kwargs)
    return wrapper


def render_error(func):
    """Render any ApiErrors raised by the method as output.

    This avoid the need for redundent try/catch blocks for
    each endpoint.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except avalon.exc.ApiError, e:
            return self._get_output(err=e)
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

    def _get_output(self, res=None, err=None):
        """Render results or an error as an iterable."""
        out = RequestOutput()
        if res is not None:
            out.results = res
        if err is not None:
            out.error = err
        return out.render()

    def _reduce(self, sets):
        """Find the intersection of all of the given non-None sets."""
        return functools.reduce(
            lambda x, y: x.intersection(y),
            [res_set for res_set in sets if res_set is not None])

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
        set_http_status(503)
        return "NONONO"

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=JSONOutHandler())
    @render_error
    @application_ready
    def albums(self, *args, **kwargs):
        """Return a list of all albums."""
        return self._get_output(res=self._albums.all())

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=JSONOutHandler())
    @render_error
    @application_ready
    def artists(self, *args, **kwargs):
        """Return a list of all artists."""
        return self._get_output(res=self._artists.all())

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=JSONOutHandler())
    @render_error
    @application_ready
    def genres(self, *args, **kwargs):
        """Return a list of all genres."""
        return self._get_output(res=self._genres.all())

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=JSONOutHandler())
    @render_error
    @application_ready
    def songs(self, *args, **kwargs):
        """Return song results based on the given query string parameters."""
        filters = RequestParams.get_from_qs(kwargs)
        
        # If there are no query string params to filter then short
        # circuit and just return all tracks
        if filters.is_empty():
            return self._get_output(res=self._tracks.all())

        sets = []

        if None is not filters.album:
            sets.append(
                self._tracks.by_album(
                    self._id_cache.get_album_id(filters.album)))
        if None is not filters.artist:
            sets.append(
                self._tracks.by_artist(
                    self._id_cache.get_artist_id(filters.artist)))
        if None is not filters.genre:
            sets.append(
                self._tracks.by_genre(
                    self._id_cache.get_genre_id(filters.genre)))

        if None is not filters.album_id:
            sets.append(self._tracks.by_album(filters.album_id))
        if None is not filters.artist_id:
            sets.append(self._tracks.by_artist(filters.artist_id))
        if None is not filters.genre_id:
            sets.append(self._tracks.by_genre(filters.genre_id))

        # Return the intersection of any none-None sets
        return self._get_output(res=self._reduce(sets))


class RequestOutput(object):

    """Render query results or errors in a format that can be serialized
    to JSON.
    """

    def __init__(self):
        """Initialize errors and results from this query."""
        self.error = None
        self.results = []

    def _format_error(self, err):
        """Format a query error (if there was one)."""
        out = {
            'is_error': False,
            'error_name': '',
            'error_msg': ''
            }
        if err is not None:
            out['is_error'] = True
            out['error_name'] = err.name
            out['error_msg'] = err.message
            self._set_error_status(err)
        return out
        
    def _format_results(self, res):
        """Format query results (if any)."""
        out = {
            'result_count': 0,
            'results': []
            }
        
        # The standard JSON encoder doesn't know how
        # to render set objects, which is what the service
        # layer returns, so we convert them to lists.
        if res is not None:
            out['result_count'] = len(res)
            out['results'] = list(res)
        return out

    def _set_error_status(self, err):
        """Set and HTTP status for the current request if this error
        has one that makes sense.
        """
        code = err.http_code
        if code != 0:
            # Set the status of the currently processing request
            # while still allowing us to render our JSON payload
            # with further information about the error
            set_http_status(code)

    def render(self):
        """Format any results or errors as a dictionary to be turned into a
        JSON payload.
        """
        err = self._format_error(self.error)
        res = self._format_results(self.results)

        return {
            'is_error': err['is_error'],
            'error_name': err['error_name'],
            'error_msg': err['error_msg'],
            'result_count': res['result_count'],
            'results': res['results']
            }


class ParamValidation(object):

    """ """

    def __init__(self, params):
        """ """
        self._params = params

    def get_as_int(self, field):
        """ """
        val = self._get(self._params, field)
        # None value indicates that this was a valid field
        # but it wasn't set (no included in the request query
        # string).
        if val is None:
            return 0

        try:
            return int(val)
        except ValueError:
            raise avalon.exc.InvalidParameterError(
                avalon.err.ERROR_INVALID_FIELD_VALUE(field))

    def get(self, field):
        """ """
        try:
            return getattr(self._params, field)
        except AttributeError:
            raise avalon.exc.InvalidParameterError(
                avalon.err.ERROR_INVALID_FIELD(field))


class RequestParams(object):
    
    """Parse and encapsulate object IDs and names from query string 
    parameters.
    """

    id_params = frozenset(['album_id', 'artist_id', 'genre_id'])
    """URL params for fetching elements by IDs"""

    name_params = frozenset(['album', 'artist', 'genre'])
    """URL params for fetching elements by name"""

    def __init__(self):
        """ Initialize values for object IDs to None."""
        self.album = None
        self.album_id = None
        self.artist = None
        self.artist_id = None
        self.genre = None
        self.genre_id = None

        self.direction = None
        self.limit = None
        self.order = None
        self.offset = None

    def __str__(self):
        """String representation of these request params."""
        return (
            'RequestParams ['
            'album: %s, '
            'album_id: %s, '
            'artist: %s, '
            'artist_id: %s, '
            'genre: %s, '
            'genre_id: %s]') % (
            self.album,
            self.album_id,
            self.artist,
            self.artist_id,
            self.genre,
            self.genre_id)

    def is_empty(self):
        """Return true if the request has no keyword parameters,
        false otherwise.
        """
        return (
            self.album is None
            and self.album_id is None 
            and self.artist is None
            and self.artist_id is None 
            and self.genre is None
            and self.genre_id is None)

    @classmethod
    def get_from_qs(cls, kwargs):
        """Construct a new filter based on query string parameters.

        Recognized params: album, album_id, artist, artist_id, genre,
        genre_id
        """
        params = cls()

        for field in cls.name_params:
            if field not in kwargs:
                continue
            setattr(params, field, kwargs[field])
        for field in cls.id_params:
            if field not in kwargs:
                continue
            try:
                val_id = int(kwargs[field])
            except ValueError:
                raise avalon.exc.InvalidParameterError(
                    avalon.err.ERROR_INVALID_FIELD_VALUE(field))
            setattr(params, field, val_id)
        return params


class _SortHelper(object):
        
    """Object meant to be used as a comparison function
    for objects based on their attributes.

    Doing sorting this way allows more flexibility than
    implementing the __cmp__ method for each object since
    that limits sorting to a single field.
    """        
    def __init__(self, field, direction):
        """Set the field to be used for sorting and the
        direction to sort.

        The sort direction is expected to be either ASC
        or DESC (case doesn't matter).
        """
        self.field = field
        self.direction = direction        
        
    def __call__(self, o1, o2):
        """Return the results of cmp() on the field of
        the two given objects, reversing it if we are
        sorting in descending order.
        """        
        v1 = getattr(o1, self.field)
        v2 = getattr(o2, self.field)

        res = cmp(v1, v2)
        if 'desc' == self.direction.lower():
            return -res
        return res


def get_sorted(elms, field, direction='asc'):
    """Sort the given elements based on the given field, optionally
    sorting them in descending order (instead of ascending).

    If the given field doesn't exist on any of the elements, no
    attempt is made to catch the resulting AttributeError.
    """
    helper = _SortHelper(field, direction)
    out = list(elms)
    out.sort(cmp=helper)
    return out

    
def get_limited(elms, limit, offset=0):
    """Apply the given limit and offset to the results.
    
    Limit and offset must be non-negative integers.
    """
    try:
        limit = int(limit)
    except ValueError:
        raise ValueError('Limit must be an integer')

    try:
        offset = int(offset)
    except ValueError:
        raise ValueError('Offset must be an integer')

    if limit < 0:
        raise ValueError('Limit must be non-negative')
    if offset < 0:
        raise ValueError('Offset must be non-negative')

    out = list(elms)
    start = offset
    end = offset + limit
    return out[start:end]

