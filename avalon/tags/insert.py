# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Functionality for loading various audio tag metadata into the database."""

from __future__ import absolute_import, unicode_literals
import sys

import sqlalchemy.exc
from avalon.packages import six
import avalon.exc
import avalon.util


def _flush_session(session):
    """Issue any pending changes in the session to the database.

    We do this to attempt to uncover potential transient errors (such
    as not having write access) with the database as soon as possible
    when writing new entries.
    """
    try:
        session.flush()
    except sqlalchemy.exc.OperationalError as e:
        six.reraise(
            avalon.exc.OperationalError,
            avalon.exc.OperationalError('{0}'.format(e)),
            sys.exc_info()[2])


class TrackFieldLoader(object):
    """Create and insert entries for the associated data for each tag
    (albums, artists, genres).
    """

    def __init__(self, session, tags):
        """Set the database session and tags to insert.

        :param sqlalchemy.orm.Session session: Database session to use.
        :param list tags: List of audio metadata namedtuples. See the
            types in :mod:`avalon.tags.read` for more information.
        """
        self._session = session
        self._tags = tags

    def insert(self, cls, id_gen, field):
        """Insert entries for the associated data for each tag using the
        given model class, ID generator, and field of the metadata tag.

        Note that this method will attempt to flush newly created entries
        to the database. If the current session is in the context of a
        transaction, the state of the transaction will not be affected.

        :param type cls: Model class to create instances of to insert
        :param function id_gen: Unique, stable ID generator
        :param unicode field: Name of the tag field to get values from
        :raises avalon.exc.OperationalError: If there are issues flushing
            newly create objects to the database.
        """
        queued = {}
        for tag in self._tags:
            # Create new models from each bit of tag metadata
            # and remove duplicates by unique ID
            obj = self._get_new_obj(cls, id_gen, field, tag)
            queued[obj.id] = obj

        self._session.add_all(list(queued.values()))
        _flush_session(self._session)

    @staticmethod
    def _get_new_obj(model_cls, id_gen, field, tag):
        """Generate a new model object for associated data for
        an audio tag.
        """
        val = getattr(tag, field, None)
        if val is None:
            # Raise an AttributeError (which would have happened
            # anyway) with some additional information to help with
            # find invalid audio tags.
            raise AttributeError(
                "Invalid tag field {0} for {1}".format(field, tag.path))
        obj = model_cls()
        obj.id = id_gen(val)
        obj.name = val
        return obj


class TrackLoader(object):
    """Create and insert entries for each tag and associated IDs.

    :cvar int write_batch_size: How many tracks to insert into a session
        at a time (between calls to flush the session).
    """
    write_batch_size = 1000

    def __init__(self, session, tags, id_cache):
        """Set the database session, tags, and ID lookup cache.

        :param sqlalchemy.orm.Session session: Database session to use.
        :param list tags: List of audio metadata namedtuples. See the
            types in :mod:`avalon.tags.read` for more information.
        """
        self._session = session
        self._tags = tags
        self._id_cache = id_cache

    def insert(self, cls, id_gen):
        """Insert entries for each audio metadata tag using the given model
        class and ID generator along with associated IDs for albums, artists,
        and genres.

        Note that this method will attempt to flush newly created entries to
        the database in batches as determined by ``write_batch_size``. If the
        current session is in the context of a transaction, the state of the
        transaction will not be affected.

        :param type cls: Model class to create instances of to insert.
        :param function id_gen: Unique, stable ID generator
        :raises avalon.exc.OperationalError: If there are issues flushing
            newly create objects to the database.
        """
        for batch in avalon.util.partition(self._tags, self.write_batch_size):
            self._insert_batch(cls, id_gen, batch)

    def _insert_batch(self, cls, id_gen, batch):
        """Insert new instances of the given class using the tag metadata
        contained in the given batch, flushing the session afterwards.
        """
        queued = []
        for tag in batch:
            queued.append(self._get_new_obj(cls, id_gen, tag))
        self._session.add_all(queued)
        _flush_session(self._session)

    def _get_new_obj(self, cls, id_gen, tag):
        """Generate a new model object for an audio tag and set the associated
        IDs for albums, artists, and genres.
        """
        obj = cls()
        obj.id = id_gen(tag.path)
        obj.name = tag.title
        obj.length = tag.length
        obj.track = tag.track
        obj.year = tag.year

        obj.album_id = self._id_cache.get_album_id(tag.album)
        obj.artist_id = self._id_cache.get_artist_id(tag.artist)
        obj.genre_id = self._id_cache.get_genre_id(tag.genre)

        return obj


class Cleaner(object):
    """Cleaner for removing already inserted entities."""

    def __init__(self, session):
        """Set the database session.

        :param sqlalchemy.orm.Session session: Database session to use.
        """
        self._session = session

    def clean_type(self, cls):
        """Delete all entities of the given class."""
        try:
            self._session.query(cls).delete()
        except sqlalchemy.exc.OperationalError as e:
            six.reraise(
                avalon.exc.OperationalError,
                avalon.exc.OperationalError('{0}'.format(e)),
                sys.exc_info()[2])
