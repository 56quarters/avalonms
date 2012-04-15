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


"""
Models representing types of metadata loaded from a music collection
along with functionality to manage connections to the backing database.
"""

from sqlalchemy import (
    create_engine,
    Column,
    ForeignKey,
    Integer,
    String)

from sqlalchemy.exc import ArgumentError, OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

import avalon.errors


__all__ = [
    'Album',
    'Artist',
    'Base',
    'Genre',
    'SessionHandler',
    'Track'
    ]


class IdNameElm(object):

    """
    """

    def __init__(self, elm_id, elm_name):
        """
        """
        self._id = elm_id
        self._name = elm_name

    @property
    def id(self):
        """
        """
        return self._id

    @property
    def name(self):
        """
        """
        return self._name

    def __eq__(self, o):
        """
        """
        if not isinstance(o, self.__class__):
            return False
        return o.id == self.id and o.name == self.name

    def __hash__(self):
       """
       """
       return hash(self.id) ^ (hash(self.name) * 7)


class TrackElm(IdNameElm):

    """
    """

    def __init__(self, t_id, t_name, t_track, t_year,
                 t_album, t_album_id, t_artist, t_artist_id,
                 t_genre, t_genre_id):
        """
        """
        super(TrackElm, self).__init__(t_id, t_name)

        self._track = t_track
        self._year = t_year
        self._album = t_album
        self._album_id = t_album_id
        self._artist = t_artist
        self._artist_id = t_artist_id
        self._genre = t_genre
        self._genre_id = t_genre_id

    @property
    def track(self):
        """
        """
        return self._track

    @property
    def year(self):
        """
        """
        return self._year

    @property
    def album(self):
        """
        """
        return self._album

    @property
    def album_id(self):
        """
        """
        return self._album_id

    @property
    def artist(self):
        """
        """
        return self._artist

    @property
    def artist_id(self):
        """
        """
        return self._artist_id
    
    @property
    def genre(self):
        """
        """
        return self._genre
    
    @property
    def genre_id(self):
        """
        """
        return self._genre_id


class Base(object):

    """ A Base for all models that defines name
        and id fields.
    """

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_elm(self):
        """
        """
        return IdNameElm(self.id, self.name)


Base = declarative_base(cls=Base)


class Track(Base):
    
    """ Model representing metadata of a media file with
        relations to other entities (album, artist, genre).
    """
    
    __tablename__ = 'tracks'
 
    track = Column(Integer)
    year = Column(Integer)

    album_id = Column(Integer, ForeignKey('albums.id'), index=True)
    artist_id = Column(Integer, ForeignKey('artists.id'), index=True)
    genre_id = Column(Integer, ForeignKey('genres.id'), index=True)

    album = relationship('Album', backref='tracks', lazy='joined', order_by='Track.id')
    artist = relationship('Artist', backref='tracks', lazy='joined', order_by='Track.id')
    genre = relationship('Genre', backref='tracks', lazy='joined', order_by='Track.id')

    def to_elm(self):
        """
        """
        return TrackElm(self.id, self.name, self.track, self.year,
                        self.album.name, self.album_id, self.artist.name,
                        self.artist_id, self.genre.name, self.genre_id)


class Album(Base):
    
    """ Model that represents the album of a song.
    """
    
    __tablename__ = 'albums'


class Artist(Base):

    """ Model that represents the artist of a song.
    """

    __tablename__ = 'artists'


class Genre(Base):

    """ Model that represents the genre of a song.
    """

    __tablename__ = 'genres'


class SessionHandler(object):

    """ Wrapper for connecting to a database and generating
        new sessions.
    """

    def __init__(self, url):
        """ Initialize the session factory and database connection.
        """
        self._url = url
        self._session_factory = sessionmaker()
        self._engine = None

    def close(self, session):
        """Safely close a session."""
        if session is None:
            return
        session.close()

    def connect(self, clean=False):
        """ Connect to the database and configure the session
            factory to use the connection, and create any needed
            tables (optionally dropping them first).
        """
        try:
            # Attempt to connect to the engine immediately after it
            # is created in order to make sure it's valid and flush
            # out any errors we're going to encounter before trying
            # to create tables or insert into it.
            self._engine = create_engine(self._url)
            self.validate()
        except ArgumentError, e:
            raise avalon.errors.ConnectionError(
                'Invalid database path or URL %s' % self._url)
        except OperationalError, e:
            raise avalon.errors.ConnectionError(
                'Could not connect to database URL %s' % self._url)
        except ImportError, e:
            raise avalon.errors.ConnectionError(
                'Invalid database connector', e)

        self._session_factory.configure(bind=self._engine)

        if clean:
            Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)

    def validate(self):
        """Ensure our database engine is valid by attempting a connection."""
        conn = None
        
        try:
            conn = self._engine.connect()
        finally:
            self.close(conn)

    def get_session(self):
        """ Get a new session.
        """
        return self._session_factory()

    
