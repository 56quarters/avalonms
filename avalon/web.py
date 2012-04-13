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


class AvalonServer(object):
    pass


class RequestFilter(object):
    
    """
    """
    
    def __init__(self):
        """
        """
        self.album_id = 0
        self.artist_id = 0
        self.genre_id = 0
        self.album = ''
        self.artist = ''
        self.genre = ''

    def __repr__(self):
        """
        """
        return (
            '<%s: '
            'album_id=%s, '
            'artist_id=%s, '
            'genre_id=%s, '
            'album=%s, '
            'artist=%s, '
            'genre=%s>') % (
            self.__class__.__name__,
            self.album_id,
            self.artist_id,
            self.genre_id,
            self.album,
            self.artist,
            self.genre)
        
    @classmethod
    def from_params(cls, *args, **kwargs):
        f = cls()

        for field in ('album_id', 'artist_id', 'genre_id'):
            if field in kwargs:
                try:
                    setattr(f, field, int(kwargs[field]))
                except ValueError:
                    setattr(f, field, 0)
        for field in ('album', 'artist', 'genre'):
            if field in kwargs:
                setattr(f, field, kwargs[field])

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
        filters = RequestFilter.from_params(*args, **kwargs)
        session = self._session_handler.get_session()

        try:
            res = session.query(Track)
            if 0 != filters.album_id:
                res = res.filter(Track.album_id == filters.album_id)
            if 0 != filters.artist_id:
                res = res.filter(Track.artist_id == filters.artist_id)
            if 0 != filters.genre_id:
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
        sess = self.session()

        try:
            res = sess.query(Artist)
            out = res.all()
        finally:
            sess.close()
        return self.list_to_json(out)
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def albums(self, *args, **kwargs):
        """
        """
        out = []
        sess = self.session()

        try:
            res = sess.query(Album)
            out = res.all()
        finally:
            sess.close()
        return self.list_to_json(out)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def genres(self, *args, **kwargs):
        """
        """
        out = []
        sess = self.session()

        try:
            res = sess.query(Genre)
            out = res.all()
        finally:
            sess.close()
        return self.list_to_json(out)

