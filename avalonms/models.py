# -*- coding: utf-8 -*-
#

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String)

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

    comment = Column(String)
    track = Column(Integer)
    year = Column(Integer)
    


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

