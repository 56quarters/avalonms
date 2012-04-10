# -*- coding: utf-8 -*-
#

from sqlalchemy import (
    create_engine,
    Column,
    ForeignKey,
    Integer,
    String)

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class Base(object):

    """
    """

    id = Column(Integer, primary_key=True)
    name = Column(String)


Base = declarative_base(cls=Base)


class Track(Base):
    
    """
    """
    
    __tablename__ = 'tracks'

    track = Column(Integer)
    year = Column(Integer)

    #album = Column(Integer, ForeignKey('albums.id'))
    #artist = Column(Integer, ForeignKey('artists.id'))
    #genre = Column(Integer, ForeignKey('genres.id'))



class Artist(Base):

    """
    """

    __tablename__ = 'artists'


class Album(Base):
    
    """
    """
    
    __tablename__ = 'albums'


class Genre(Base):

    """
    """

    __tablename__ = 'genres'


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
        self._session_factory.configure(bind=self._engine)

    def create_tables(self):
        """
        """
        Base.metadata.create_all(self._engine)

    def get_session(self):
        """
        """
        return self._session_factory()


