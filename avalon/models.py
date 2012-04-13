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

from sqlalchemy.orm import backref, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


__all__ = [
    'Album',
    'Artist',
    'Base',
    'Genre',
    'Track'
    ]


class Base(object):

    """
    """

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_json(self):
        """
        """
        return {
            'id': self.id,
            'name': self.name}


Base = declarative_base(cls=Base)


class Track(Base):
    
    """
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
        """
        """
        base = super(Track, self).to_json()
        base['track'] = self.track
        base['year'] = self.year
        base['album'] = self.album.name
        base['artist'] = self.artist.name
        base['genre'] = self.genre.name
        return base


class Album(Base):
    
    """
    """
    
    __tablename__ = 'albums'
    #tracks = relationship('Track', order_by='Track.id', backref='album')


class Artist(Base):

    """
    """

    __tablename__ = 'artists'
    #tracks = relationship('Track', order_by='Track.id', backref='artist')


class Genre(Base):

    """
    """

    __tablename__ = 'genres'
    #tracks = relationship('Track', order_by='Track.id', backref='genre')


class SessionHandler(object):

    def __init__(self):
        """
        """
        self._session_factory = sessionmaker()
        self._engine = None

    def connect(self):
        """
        """
        self._engine = create_engine('sqlite:////tmp/avalonms.sqlite', echo=True)
        #self._engine = create_engine('sqlite:///:memory:', echo=True)
        self._session_factory.configure(bind=self._engine)

    def create_tables(self):
        """
        """
        Base.metadata.create_all(self._engine)

    def get_session(self):
        """
        """
        return self._session_factory()


