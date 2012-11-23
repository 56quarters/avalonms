# -*- coding: utf-8 -*-
#
# Avalon Music Server
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
    'UUIDType'
    ]


class UUIDType(TypeDecorator):
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

    id = Column(UUIDType, primary_key=True)
    name = Column(String)


Base = declarative_base(cls=_Base)


class Track(Base):
    
    """Model representing metadata of a media file with
    relations to other entities (album, artist, genre).
    """
    
    __tablename__ = 'tracks'
 
    track = Column(Integer)
    year = Column(Integer)

    album_id = Column(UUIDType, ForeignKey('albums.id'), index=True)
    artist_id = Column(UUIDType, ForeignKey('artists.id'), index=True)
    genre_id = Column(UUIDType, ForeignKey('genres.id'), index=True)

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
        to use the connection, and create any needed tables (optionally
        dropping them first).
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

