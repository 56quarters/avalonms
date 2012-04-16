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


""" HTTP frontend for handling requests."""


import logging

import cherrypy
from cherrypy.wsgiserver import CherryPyWSGIServer


import avalon.models
import avalon.services
import avalon.views


__all__ = [
    'AvalonServerConfig',
    'AvalonServer',
    'AvalonHandler',
    'RequestFilter'
    ]


class JSONOutHandler(object):

    """
    """

    def __init__(self):
        """
        """
        self._encoder = avalon.views.JSONEncoder()

    def __call__(self, *args, **kwargs):
        """
        """
        value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
        return self._encoder.encode(value)


class AvalonServerConfig(object):

    """ Configuration for our HTTP server.
    """

    def __init__(self):
        self.log = None
        self.bind_addr = None
        self.gateway = None


class AvalonServer(CherryPyWSGIServer):

    """ Wrap the standard CherryPy server to use our own
        error logging mechanism.
    """

    def __init__(self, config):
        """ Call the parent constructor and set our error logger.
        """
        super(AvalonServer, self).__init__(config.bind_addr, config.gateway)
        self._log = config.log

    def error_log(self, msg='', level=logging.INFO, trackback=False):
        """ Write an error to the log, optionally with a traceback.
        """
        if traceback:
            msg = '%s: %s' % (msg, traceback.format_exc())
        self._log.log(level, msg)


class AvalonHandler(object):

    """ Handle HTTP requests and return result sets in JSON.
    """

    def __init__(self, session_handler):
        """ Set the session handler and optionally, cache to use.
        """
        self._tracks = avalon.services.TrackStore(session_handler)
        self._albums = avalon.services.AlbumStore(session_handler)
        self._artists = avalon.services.ArtistStore(session_handler)
        self._genres = avalon.services.GenreStore(session_handler)
        self._id_cache = avalon.services.IdLookupCache(session_handler)

    def _get_output(self, res=None, err=None):
        """ Render results or an error as an iterable.
        """
        out = RequestOutput()
        if res is not None:
            out.results = res
        if err is not None:
            out.error = err
        return out.render()

    def _reduce(self, *args):
        """ Find the intersection of all of the given non-None sets.
        """
        set_intersect = lambda x, y: x.intersection(y)
        set_filter = lambda x: x is not None

        return reduce(set_intersect, filter(set_filter, args))

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=JSONOutHandler())
    def songs(self, *args, **kwargs):
        """ Return song results based on the given query string
            parameters.
        """
        filters = RequestParams.build(self._id_cache, kwargs)

        # If there are no query string params to filter to input
        # but short circuit and just return all tracks
        if filters.is_empty():
            return self._get_output(self._tracks.all())

        set1 = None
        set2 = None
        set3 = None

        if None is not filters.album_id:
            set1 = self._tracks.by_album(filters.album_id)
        if None is not filters.artist_id:
            set2 = self._tracks.by_artist(filters.artist_id)
        if None is not filters.genre_id:
            set3 = self._tracks.by_genre(filters.genre_id)
            
        # Return the intersection of any none-None sets
        return self._get_output(res=self._reduce(set1, set2, set3))

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=JSONOutHandler())
    def albums(self, *args, **kwargs):
        """ Return a list of all albums.
        """
        return self._get_output(res=self._albums.all())

    @cherrypy.expose
    @cherrypy.tools.json_out(handler=JSONOutHandler())
    def artists(self, *args, **kwargs):
        """ Return a list of all artists.
        """
        return self._get_output(res=self._artists.all())
        
    @cherrypy.expose
    @cherrypy.tools.json_out(handler=JSONOutHandler())
    def genres(self, *args, **kwargs):
        """ Return a list of all genres.
        """
        return self._get_output(res=self._genres.all())


class RequestOutput(object):

    """ Render query results or errors in a format that can
        be serialized to JSON.
    """

    def __init__(self):
        """
        """
        self.error = None
        self.results = []

    def _format_error(self, err):
        """
        """
        out = {
            'error': False,
            'error_code': 0,
            'error_msg': ''
            }
        if err is not None:
            out['error'] = True
            out['error_code'] = err.code
            out['error_msg'] = err.message
        return out
        
    def _format_results(self, res):
        """
        """
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

    def render(self):
        """
        """
        err = self._format_error(self.error)
        res = self._format_results(self.results)

        return {
            'error': err['error'],
            'error_code': err['error_code'],
            'error_msg': err['error_msg'],
            'result_count': res['result_count'],
            'results': res['results']
            }


class RequestParams(object):
    
    """ Parse and encapsulate object IDs and names from
        query string parameters.
    """
    
    def __init__(self):
        """ Initialize values for object IDs to None.
        """
        self.album_id = None
        self.artist_id = None
        self.genre_id = None

    def is_empty(self):
        """
        """
        return self.album_id is None and self.artist_id is None and self.genre_id is None

    @classmethod
    def build(cls, cache, kwargs):
        """ Construct a new filter based on the given query
            string parameters and name to ID cache.

            Recognized params: album, album_id, artist, artist_id,
            genre, genre_id
        """
        f = cls()

        for field in ('album', 'artist', 'genre'):
            if field not in kwargs:
                continue
            # Look up a value from the cache and use it to filter
            # the results. We don't care if the cache returned a
            # valid ID since we want the request to return 0
            # results for bad QS params.
            val_id = cache.get_id(field, kwargs[field])
            setattr(f, field + '_id', val_id)

        for field in ('album_id', 'artist_id', 'genre_id'):
            if field not in kwargs:
                continue
            try:
                val_id = int(kwargs[field])
            except ValueError:
                # Use an invalid ID anyway since we want the
                # request to return 0 results for bad QS params.
                val_id = 0
            setattr(f, field, val_id)
        return f

