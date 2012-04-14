# -*- coding: utf-8 -*-
#


"""
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
    'ConnectionError',
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

    def to_json(self):
        """ Return a representation of this object using builtin
            data structures that can be easily serialized.
        """
        return {
            'id': self.id,
            'name': self.name}


Base = declarative_base(cls=Base)


class Track(Base):
    
    """ Model representing metadata of a media file with
        relations to other entities (album, artist, genre).
    """
    
    __tablename__ = 'tracks'

    track = Column(Integer)
    year = Column(Integer)

    album_id = Column(Integer, ForeignKey('albums.id'))
    artist_id = Column(Integer, ForeignKey('artists.id'))
    genre_id = Column(Integer, ForeignKey('genres.id'))

    album = relationship('Album', backref='tracks', lazy='joined', order_by='Track.id')
    artist = relationship('Artist', backref='tracks', lazy='joined', order_by='Track.id')
    genre = relationship('Genre', backref='tracks', lazy='joined', order_by='Track.id')

    def to_json(self):
        """ Return a representation of this track including
            the album, artist, and genre.
        """
        base = super(Track, self).to_json()
        base['track'] = self.track
        base['year'] = self.year
        base['album'] = self.album.name
        base['artist'] = self.artist.name
        base['genre'] = self.genre.name
        return base


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

    def __init__(self, url, verbose=False):
        """ Initialize the session factory and database connection.
        """
        self._url = url
        self._verbose = verbose
        self._session_factory = sessionmaker()
        self._engine = None

    def connect(self):
        """ Connect to the database and configure the session
            factory to use the connection.
        """
        try:
            self._engine = create_engine(self._url, echo=self._verbose)
        except (ArgumentError, OperationalError), e:
            raise avalon.errors.ConnectionError(
                'Could not connect to database', e)
        except ImportError, e:
            raise avalon.errors.ConnectionError(
                'Invalid database connector', e)
        self._session_factory.configure(bind=self._engine)

    def create_tables(self):
        """ Create tables for each model if they haven't already 
            been created.
        """
        Base.metadata.create_all(self._engine)

    def get_session(self):
        """ Get a new session.
        """
        return self._session_factory()


