# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""
Models representing types of metadata loaded from a music collection
along with functionality to manage connections to the backing database.
"""

from __future__ import absolute_import, unicode_literals
import uuid
import sys
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
from sqlalchemy.exc import ArgumentError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import avalon.exc
import avalon.log
from avalon.packages import six


# Ignore pylint warning about abstract method since overriding it
# is optional and SQLAlchemy will do the right thing if it is missing.
# pylint: disable=abstract-method,too-many-public-methods
class _UuidType(TypeDecorator):
    """Platform-independent GUID type.

    See http://docs.sqlalchemy.org/en/rel_0_9/core/types.html
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
            return '%s' % value
        elif not isinstance(value, uuid.UUID):
            return "%.32x" % uuid.UUID(value)
        return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)


class _BaseFields(object):
    """A base for all models that define name (string) and id (UUID) fields."""
    # pylint: disable=invalid-name
    id = Column(_UuidType, primary_key=True)
    name = Column(String)


# Declarative base that also includes id and name fields
# (common to all meta data types) that should be used as
# the base for all models. Ignore pylint warning about invalid
# name since this is a class, not a constant.
# pylint: disable=invalid-name
_Base = declarative_base(cls=_BaseFields)


# pylint: disable=no-init
class Track(_Base):
    """Model representing metadata of a media file with relations to other
    entities (album, artist, genre).

    :ivar uuid.UUID id: UUID of this track
    :ivar unicode name: Name of this track
    :ivar int length: Length of this track in seconds
    :ivar int track: Track number on an album
    :ivar int year: Year the track was released in
    :ivar uuid.UUID album_id: UUID referencing the album the track appeared on
    :ivar uuid.UUID artist_id: UUID referencing the artist the track is by
    :ivar uuid.UUID genre_id: UUID referencing the genre the track belongs to
    :ivar Album album: Lazy join-loaded album reference
    :ivar Artist artist: Lazy join-loaded artist reference
    :ivar Genre genre: Lazy join-loaded genre reference
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


# pylint: disable=no-init
class Album(_Base):
    """Model that represents the album of a song.

    :ivar uuid.UUID id: UUID based on the name of this album
    :ivar unicode name: Name of this album
    """

    __tablename__ = 'albums'


# pylint: disable=no-init
class Artist(_Base):
    """Model that represents the artist of a song.

    :ivar uuid.UUID id: UUID based on the name of this artist
    :ivar unicode name: Name of this artist
    """

    __tablename__ = 'artists'


# pylint: disable=no-init
class Genre(_Base):
    """Model that represents the genre of a song.

    :ivar uuid.UUID id: UUID based on the name of this genre
    :ivar unicode name: Name of this genre
    """

    __tablename__ = 'genres'


def get_engine(url, factory=None):
    """Get a database engine for the given URL, mapping expected
    SQLAlchemy exceptions to our own.

    :param str url: Database connection string
    :param callable factory: Factory method to create the SQLAlchemy
        Engine instance. If not specified the :func:`create_engine`
        function will be used. This parameter should only be passed
        for unit testing.
    :return: Database engine based on the connection string
    :rtype: sqlalchemy.engine.Engine
    :raises avalon.exc.ConnectionError: If the URL is malformed or the
        specified database adapter is not available (meaning it could
        not be imported).
    """
    if factory is None:
        factory = create_engine
    try:
        return factory(url)
    except ArgumentError as e:
        raise avalon.exc.ConnectionError(
            'Invalid connection URL: %s' % e)
    except ImportError as e:
        raise avalon.exc.ConnectionError(
            'Invalid database adapter: %s' % e)


def get_metadata():
    """Accessor for metadata about the base for all models.

    :return: Meta data describing all declared schemas
    :rtype: sqlalchemy.schema.MetaData
    """
    return _Base.metadata


def get_session_factory():
    """Get a new session factory callable.

    :return: New session factory implementation
    :rtype: sqlalchemy.schema.MetaData
    """
    return sessionmaker()


class SessionHandlerConfig(object):
    """Configuration for the handler.

    :ivar sqlalchemy.engine.Engine engine: Database engine to use
    :ivar sqlalchemy.schema.MetaData metadata: Database meta data
    :ivar sqlalchemy.schema.MetaData session_factory: Session factory
        to use
    """

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.metadata = None


class SessionHandler(object):
    """Wrapper for connecting to a database and generating
    new sessions.
    """

    _logger = avalon.log.get_error_log()

    def __init__(self, config):
        """Set the database engine, session factory, associated model metadata
        and logger to use for this session handler.

        :param SessionHandlerConfig config: Configuration for this session handler
        """
        self._engine = config.engine
        self._session_factory = config.session_factory
        self._metadata = config.metadata

    def close(self, session):
        """Safely close a session, logging any :class:`SQLAlchemyError` based
        exceptions encountered.

        :param session: Session or connection that has a .close() method
        """
        if session is None:
            return
        try:
            session.close()
        except SQLAlchemyError as e:
            self._logger.warn('Problem closing session: %s', e, exc_info=True)

    def connect(self):
        """Connect to the database and configure the session factory
        to use the connection, and create any needed tables (if they
        do not already exist).

        Required tables for all models will be created if they do not already
        exist. If they do exist, they will not be modified or altered.

        :raises avalon.exc.ConnectionError: If there was a problem connecting
            to the database.
        :raises avalon.exc.OperationalError: If there was a problem creating
            any of the needed tables for models.
        """
        try:
            # Attempt to connect to the engine to make sure it's valid and
            # flush out any errors we're going to encounter before trying
            # to create tables or insert into it.
            self.validate()
        except OperationalError as e:
            six.reraise(
                avalon.exc.ConnectionError,
                avalon.exc.ConnectionError(
                    'Could not connect to %s database: %s' % (self._engine.name, e)),
                sys.exc_info()[2])

        self._session_factory.configure(bind=self._engine)

        try:
            # Attempt to catch and wrap errors here related to not being able
            # to create tables for each model. It's entirely possible that the
            # tables already exist and we won't actually encounter a permission
            # error until we try to rescan (and delete / insert) a collection.
            self._metadata.create_all(self._engine)
        except OperationalError as e:
            six.reraise(
                avalon.exc.OperationalError,
                avalon.exc.OperationalError(
                    'Could not initialize required schema: %s' % e),
                sys.exc_info()[2])

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

    @contextmanager
    def scoped_session(self, read_only=True):
        """Get a new session from the session factory that acts as a context
        manager and is automatically cleaned up after use.

        The session will be automatically committed on success if read_only is
        set to False, automatically rolled back if read_only is set to False
        and any exceptions are raised, and automatically cleaned up no matter
        what.

        Note that any objects associated with the returned session will be
        detached (and hence invalid) if read_only is set to False and the
        session is committed.

        :param bool read_only: If true, don't commit or rollback the session
        :return: A session that will be cleaned up by a context manager
        :rtype: sqlalchemy.orm.Session
        """
        conn = None

        try:
            conn = self._session_factory()
            yield conn
            # Don't commit if this is a read_only session since that will
            # invalidate the fetched objects (even non-relation properties)
            # which are probably going to be used for something after the
            # session is closed (like populating some in-memory store).
            if not read_only:
                self._logger.debug('Non-read only transaction, committing')
                conn.transaction.commit()
        except:
            if not read_only and conn is not None:
                self._logger.debug('Error during non-read only transaction, rollback')
                conn.transaction.rollback()
            raise
        finally:
            self.close(conn)


class ReadOnlyDao(object):
    """Read-only DAO for loading each type of model object by
    making use of the :class:`SessionHandler` and each associated
    model class.

    This class doesn't add a lot of functionality on top of the
    :class:`SessionHandler`, it's just a facade to allow consumers
    to be tested more easily.

    :cvar int read_batch_size: Number of results to yield at a time
        when loading albums, artists, genres, or tracks.
    """
    read_batch_size = 1000

    def __init__(self, session_handler):
        """Set the session handler to use for fetching models."""
        self._session_handler = session_handler

    def get_all_albums(self, session=None):
        """Get a generator that yields all Album models in the database.

        :param sqlalchemy.orm.Session session: Optional existing
            session to use for fetching rows instead of using
            a new connection
        :return: Generator to get all albums in batches
        :rtype: sqlalchemy.orm.Query
        """
        return self._get_all_cls(Album, session=session)

    def get_all_artists(self, session=None):
        """Get a generator that yields all Artist models in the database.

        :param sqlalchemy.orm.Session session: Optional existing
            session to use for fetching rows instead of using
            a new connection
        :return: Generator to get all artists in batches
        :rtype: sqlalchemy.orm.Query
        """
        return self._get_all_cls(Artist, session=session)

    def get_all_genres(self, session=None):
        """Get a generator that yields all Genre models in the database.

        :param sqlalchemy.orm.Session session: Optional existing
            session to use for fetching rows instead of using
            a new connection
        :return: Generator to get all genres in batches
        :rtype: sqlalchemy.orm.Query
        """
        return self._get_all_cls(Genre, session=session)

    def get_all_tracks(self, session=None):
        """Get  a generator that yields all Track models in the database.

        :param sqlalchemy.orm.Session session: Optional existing
            session to use for fetching rows instead of using
            a new connection
        :return: Generator to get all tracks in batches
        :rtype: sqlalchemy.orm.Query
        """
        return self._get_all_cls(Track, session=session)

    def _get_all_cls(self, cls, session=None):
        """Get a generator to yield models of the given class in batches."""
        if session is not None:
            return session.query(cls).yield_per(self.read_batch_size)

        with self._session_handler.scoped_session() as session:
            return session.query(cls).yield_per(self.read_batch_size)
