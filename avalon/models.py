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


from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.exc import ArgumentError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import avalon.exc


__all__ = [
    'Album',
    'Artist',
    'Base',
    'Genre',
    'SessionHandler',
    'Track'
    ]


class Base(object):

    """ A Base for all models that defines name
        and id fields.
    """

    id = Column(Integer, primary_key=True)
    name = Column(String)


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

    def __init__(self, url, log):
        """ Initialize the session factory and database connection.
        """
        self._url = url
        self._log = log
        self._session_factory = sessionmaker()
        self._engine = None

    def close(self, session):
        """Safely close a session."""
        if session is None:
            return
        try:
            session.close()
        except SQLAlchemyError, e:
            self._log.warn('Error closing session: %s', e.message, exc_info=True)

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
            raise avalon.exc.ConnectionError(
                'Invalid database path or URL %s' % self._url)
        except OperationalError, e:
            raise avalon.exc.ConnectionError(
                'Could not connect to database URL %s' % self._url)
        except ImportError, e:
            raise avalon.exc.ConnectionError(
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

    
