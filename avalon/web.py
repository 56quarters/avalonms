# -*- coding: utf-8 -*-
#

"""
"""


import cherrypy
from cherrypy.wsgiserver import CherryPyWSGIServer

import avalon.services
from avalon.models import (
    Album,
    Artist,
    Genre,
    Track)


__all__ = []


class AvalonServer(object):
    pass


class RequestFilter(object):
    
    """
    """
    
    def __init__(self):
        """
        """
        self.album_id = None
        self.artist_id = None
        self.genre_id = None

    @classmethod
    def from_params(cls, cache, kwargs):
        """
        """
        f = cls()
        for field in ('album', 'artist', 'genre'):
            if field not in kwargs:
                continue
            val_id = cache.get_id(field, kwargs[field])
            setattr(f, field + '_id', val_id)
        for field in ('album_id', 'artist_id', 'genre_id'):
            if field not in kwargs:
                continue
            try:
                val_id = int(kwargs[field])
            except ValueError:
                val_id = 0
            setattr(f, field, val_id)
        return f


class AvalonHandler(object):

    def __init__(self, session_handler):
        """
        """
        self._session_handler = session_handler
        self._id_cache = avalon.services.IdService(session_handler)
        self._id_cache.load()

    def list_to_json(self, res):
        """
        """
        return [thing.to_json() for thing in res]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def songs(self, *args, **kwargs):
        """
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
    def artists(self, *args, **kwargs):
        """
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
    def albums(self, *args, **kwargs):
        """
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
    def genres(self, *args, **kwargs):
        """
        """
        out = []
        session = self._session_handler.get_session()

        try:
            res = session.query(Genre)
            out = res.all()
        finally:
            session.close()
        return self.list_to_json(out)

