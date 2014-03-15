# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


"""
Models representing types of metadata loaded from a music collection
along with functionality to manage connections to the backing database.
"""

import uuid
from contextlib import contextmanager

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
    'Genre',
    'SessionHandler',
    'SessionHandlerConfig',
    'Track'
]


class _UuidType(TypeDecorator):
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


class _BaseFields(object):
    """A base for all models that defines name (string) and id (UUID) fields."""
    id = Column(_UuidType, primary_key=True)
    name = Column(String)


# Declarative base that also includes id and name fields
# (common to all meta data types) that should be used as
# the base for all models
_Base = declarative_base(cls=_BaseFields)


class Track(_Base):
    """Model representing metadata of a media file with relations to other
    entities (album, artist, genre).
    """

    __tablename__ = 'tracks'

    length = Column(Integer)
    track = Column(Integer)
    year = Column(Integer)

    album_id = Column(_UuidType, ForeignKey('albums.id'), index=True)
    artist_id = Column(_UuidType, ForeignKey('artists.id'), index=True)
    genre_id = Column(_UuidType, ForeignKey('genres.id'), index=True)

    # Join album, artist, and genre using an INNER JOIN whenever tracks are loaded
    album = relationship(
        'Album', backref='tracks', lazy='joined', innerjoin=True, order_by='Track.id')
    artist = relationship(
        'Artist', backref='tracks', lazy='joined', innerjoin=True, order_by='Track.id')
    genre = relationship(
        'Genre', backref='tracks', lazy='joined', innerjoin=True, order_by='Track.id')


class Album(_Base):
    """Model that represents the album of a song."""

    __tablename__ = 'albums'


class Artist(_Base):
    """Model that represents the artist of a song."""

    __tablename__ = 'artists'


class Genre(_Base):
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
    return _Base.metadata


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
        """Set the database engine, session factory, associated model metadata
        and logger to use for this session handler.
        """
        self._engine = config.engine
        self._session_factory = config.session_factory
        self._metadata = config.metadata
        self._log = config.log

    def close(self, session):
        """Safely close a session, logging any :class:`SQLAlchemyError` based
        exceptions encountered.
        """
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

        Raise a :class:`ConnectionError` if there was an issue connecting
        to the database or if the database type is invalid or unsupported.

        Required tables for all models will be created if they do not already
        exist. If they do exist, they will not be modified or altered.
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
        """Ensure our database engine is valid by attempting a connection.

        Exceptions raised here will be propagated after cleaning up any
        resources associated with the connection.
        """
        conn = None

        try:
            conn = self._engine.connect()
        finally:
            self.close(conn)

    def get_session(self):
        """Get a new session from the session factory."""
        return self._session_factory()

    @contextmanager
    def get_scoped_session(self, read_only=True):
        """Get a new session from the session factory that acts as a context
        manager and is automatically cleaned up after use.

        The session will be automatically commited on success if read_only is
        set to False, automatically rolled back if read_only is set to False
        and any exceptions are raised, and automatically cleaned up no matter
        what.

        Note that any objects associated with the returned session will be
        detached (and hence invalid) if read_only is set to False and the
        session is commited.
        """
        conn = None

        try:
            conn = self.get_session()
            yield conn
            # Don't commit if this is a read_only session since that will
            # invalidate the fetched objects (even non-relation properties)
            # which are probably going to be used for something after the
            # session is closed (like populating some in-memory store).
            if not read_only:
                conn.commit()
        except:
            if not read_only and conn is not None:
                conn.rollback()
            raise
        finally:
            self.close(conn)

