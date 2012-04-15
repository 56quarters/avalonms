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

import avalon.services
from avalon.models import (
    Album,
    Artist,
    Genre,
    Track)


__all__ = [
    'AvalonServerConfig',
    'AvalonServer',
    'AvalonHandler',
    'RequestFilter'
    ]


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

    def __init__(self, session_handler, cache=None):
        """ Set the session handler and optionally, cache to use.
        """
        if cache is None:
            cache = avalon.services.IdService(session_handler)

        self._session_handler = session_handler
        self._id_cache = cache
        self._id_cache.load()

    def get_output(self, res=None, err=None):
        """
        """
        out = RequestOutput()
        if res is not None:
            out.results = res
        
        return out.to_json()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def songs(self, *args, **kwargs):
        """ Return song results based on the given query string
            parameters.
        """
        out = []
        filters = RequestParams.build(self._id_cache, kwargs)
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
            self._session_handler.close(session)
        return self.get_output(out)

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
        return self.get_output(out)

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
            self._session_handler.close(session)
        return self.get_output(out)
        
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
            self._session_handler.close(session)
        return self.get_output(out)


class RequestOutput(object):

    """
    """

    def __init__(self):
        """
        """
        self.error = None
        self.results = []

    def format_error(self, err):
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
        
    def format_results(self, res):
        """
        """
        out = {
            'result_count': 0,
            'results': []
            }
        if res is not None:
            out['result_count'] = len(res)
            out['results'] = [thing.to_json() for thing in res]
        return out

    def to_json(self):
        """
        """
        err = self.format_error(self.error)
        res = self.format_results(self.results)

        return {
            'error': err['error'],
            'error_code': err['error_code'],
            'error_msg': err['error_msg'],
            'result_count': res['result_count'],
            'results': res['results']
            }


class RequestParams(object):
    
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

