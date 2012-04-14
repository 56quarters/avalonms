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


import cherrypy
from cherrypy.wsgiserver import CherryPyWSGIServer

import avalon.services
from avalon.models import (
    Album,
    Artist,
    Genre,
    Track)


__all__ = [
    'AvalonHandler',
    'RequestFilter'
    ]


class RequestFilter(object):
    
    """ Parse and ecapsulate object IDs and names from
        query string parameters.
    """
    
    def __init__(self):
        """ Initialize values for object IDs to None.
        """
        self.album_id = None
        self.artist_id = None
        self.genre_id = None

    @classmethod
    def from_params(cls, cache, kwargs):
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


class AvalonHandler(object):

    """ Handle HTTP requests and return result sets in JSON.
    """

    def __init__(self, session_handler, cache=None):
        """ Set the session handler and optionally, cache to use.
        """
        if cache is None:
            cache = avalon.services.IdService(session_handler)

        self._session_handler = session_handler
        self._id_cache = cache
        self._id_cache.load()

    def list_to_json(self, res):
        """ Convert a list of models to a list of dictionaries.
        """
        return [thing.to_json() for thing in res]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def songs(self, *args, **kwargs):
        """ Return song results based on the given query string
            parameters.
        """
        out = []
        filters = RequestFilter.from_params(self._id_cache, kwargs)
        session = self._session_handler.get_session()

        try:
            res = session.query(Track)
            if None is not filters.album_id:
                res = res.filter(Track.album_id == filters.album_id)
            if None is not filters.artist_id:
                res = res.filter(Track.artist_id == filters.artist_id)
            if None is not filters.genre_id:
                res = res.filter(Track.genre_id == filters.genre_id)
            out = res.join(Album).join(Artist).join(Genre).all()
        finally:
            session.close()
        return self.list_to_json(out)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def albums(self, *args, **kwargs):
        """ Return a list of all albums.
        """
        out = []
        session = self._session_handler.get_session()

        try:
            res = session.query(Album)
            out = res.all()
        finally:
            session.close()
        return self.list_to_json(out)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def artists(self, *args, **kwargs):
        """ Return a list of all artists.
        """
        out = []
        session = self._session_handler.get_session()

        try:
            res = session.query(Artist)
            out = res.all()
        finally:
            session.close()
        return self.list_to_json(out)
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def genres(self, *args, **kwargs):
        """ Return a list of all genres.
        """
        out = []
        session = self._session_handler.get_session()

        try:
            res = session.query(Genre)
            out = res.all()
        finally:
            session.close()
        return self.list_to_json(out)

