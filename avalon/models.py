# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2013 TSH Labs <projects@tshlabs.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""
Models representing types of metadata loaded from a music collection
along with functionality to manage connections to the backing database.
"""


import uuid

from sqlalchemy import (
    create_engine,
    CHAR,
    Column,
    ForeignKey,
    Integer,
    String,
    TypeDecorator)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import avalon.exc


__all__ = [
    'get_engine',
    'get_metadata',
    'get_session_factory',
    'Album',
    'Artist',
    'Base',
    'Genre',
    'SessionHandler',
    'SessionHandlerConfig',
    'Track',
    'UuidType'
    ]


class UuidType(TypeDecorator):
    """Platform-independent GUID type.

    See http://docs.sqlalchemy.org/en/rel_0_7/core/types.html
    """

    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        elif not isinstance(value, uuid.UUID):
            return "%.32x" % uuid.UUID(value)
        return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)


class _Base(object):

    """A base for all models that defines name and id fields."""

    id = Column(UuidType, primary_key=True)
    name = Column(String)


Base = declarative_base(cls=_Base)


class Track(Base):
    
    """Model representing metadata of a media file with
    relations to other entities (album, artist, genre).
    """
    
    __tablename__ = 'tracks'

    length = Column(Integer)
    track = Column(Integer)
    year = Column(Integer)

    album_id = Column(UuidType, ForeignKey('albums.id'), index=True)
    artist_id = Column(UuidType, ForeignKey('artists.id'), index=True)
    genre_id = Column(UuidType, ForeignKey('genres.id'), index=True)

    album = relationship('Album', backref='tracks', lazy='joined', order_by='Track.id')
    artist = relationship('Artist', backref='tracks', lazy='joined', order_by='Track.id')
    genre = relationship('Genre', backref='tracks', lazy='joined', order_by='Track.id')


class Album(Base):
    
    """Model that represents the album of a song."""
    
    __tablename__ = 'albums'


class Artist(Base):

    """Model that represents the artist of a song."""

    __tablename__ = 'artists'


class Genre(Base):

    """Model that represents the genre of a song."""

    __tablename__ = 'genres'


# Factory methods for the purposes of separating this
# object creation from the SessionHandler class so that
# we can test it more easily.


def get_engine(url):
    """Get a database engine for the given URL."""
    return create_engine(url)


def get_metadata():
    """Accessor for metadata about the base for all models."""
    return Base.metadata


def get_session_factory():
    """Get a new session factory callable."""
    return sessionmaker()


class SessionHandlerConfig(object):

    """Configuration for the handler."""

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.metadata = None
        self.log = None


class SessionHandler(object):

    """Wrapper for connecting to a database and generating
    new sessions.
    """

    def __init__(self, config):
        self._engine = config.engine
        self._session_factory = config.session_factory
        self._metadata = config.metadata
        self._log = config.log

    def close(self, session):
        """Safely close a session."""
        if session is None:
            return
        try:
            session.close()
        except SQLAlchemyError, e:
            self._log.warn('Problem closing session: %s', e.message, exc_info=True)

    def connect(self):
        """Connect to the database and configure the session factory
        to use the connection, and create any needed tables (if they
        do not already exist).
        """
        try:
            # Attempt to connect to the engine to make sure it's valid and
            # flush out any errors we're going to encounter before trying
            # to create tables or insert into it.
            self.validate()
        except OperationalError, e:
            raise avalon.exc.ConnectionError(
                'Could not connect to %s database' % self._engine.name, e)
        except ImportError, e:
            raise avalon.exc.ConnectionError(
                'Invalid database connector', e)

        self._session_factory.configure(bind=self._engine)
        self._metadata.create_all(self._engine)

    def validate(self):
        """Ensure our database engine is valid by attempting a connection."""
        conn = None
        
        try:
            conn = self._engine.connect()
        finally:
            self.close(conn)

    def get_session(self):
        """Get a new session."""
        return self._session_factory()

