# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#

"""Scan a music collection and insert meta data into a database."""

from __future__ import absolute_import, unicode_literals

import avalon.log
import avalon.ids
import avalon.app.factory
import avalon.tags.crawl
import avalon.tags.insert
import avalon.tags.read
from avalon.models import Album, Artist, Genre, Track


__all__ = [
    'AvalonCollectionScanner'
]


class AvalonCollectionScanner(object):
    """High-level logic for reading meta data from a music collection
    and inserting it into a SQL database of some sort.
    """
    _logger = avalon.log.get_error_log()

    def __init__(self, database, id_cache):
        """Set the database connection manager and ID-lookup cache
        to use for scanning the music collection.

        :param avalon.models.SessionHandler database: Database session
            handler to use for inserting meta data into a database.
        :param avalon.cache.IdLookupCache id_cache: In-memory store for
            looking up IDs of albums, artists, and genres based on their
            name.
        """
        self._database = database
        self._id_cache = id_cache

    def _clean_existing_tags(self, session):
        """Remove all existing meta data from the database using the
        given session.

        The session is expected to be using a transaction that will allow
        the deletion of existing data to be rolled back if needed.

        :param sqlalchemy.orm.Session session: Session to use for removing
            all existing meta data from the database.
        """
        self._logger.info("Removing old meta data...")
        cleaner = avalon.tags.insert.Cleaner(session)
        for cls in (Album, Artist, Genre, Track):
            cleaner.clean_type(cls)

    def _insert_new_tags(self, session, tag_meta):
        """Insert new entries into the album, artist, genre, and track
        tables based on the given audio tag meta data.

        The session is expected to be using a transaction that will allow
        the insertion of data to be rolled back if needed.

        :param sqlalchemy.orm.Session session: Session to use for inserting
            new meta data into the database.
        :param list tag_meta: List of :class:`avalon.tags.read.Metadata` instances
            resulting from reading audio meta data from a music collection.
        """
        self._logger.info("Inserting new tag meta data for associated attributes...")
        field_loader = avalon.tags.insert.TrackFieldLoader(session, tag_meta)
        field_loader.insert(Album, avalon.ids.get_album_id, 'album')
        field_loader.insert(Artist, avalon.ids.get_artist_id, 'artist')
        field_loader.insert(Genre, avalon.ids.get_genre_id, 'genre')

        # Note that we're passing the current session to the reload
        # method of the ID cache. This makes sure that we're loading
        # the values inserted in the current session (transaction),
        # not old already committed ones.
        self._logger.info("Building ID-name lookup for associated attributes...")
        self._id_cache.reload(session=session)

        self._logger.info("Inserting new tag meta data for songs...")
        track_loader = avalon.tags.insert.TrackLoader(session, tag_meta, self._id_cache)
        track_loader.insert(Track, avalon.ids.get_track_id)

    def scan_path(self, path):
        """Recursively scan the given path for files, attempt to read audio
        meta data from them, and insert the resulting meta data into a
        database of some sort.

        Deletion of existing meta data and insertion of new meta data is
        done within the context of a transaction such that the database
        will be left in a consistent state.

        :param str path: Relative or absolute path to a music collection
        """
        self._logger.info(
            "Crawling music collection at %s...", path)

        crawler = avalon.app.factory.new_crawler(path)
        tag_meta = crawler.get_tags()

        self._logger.info("Loaded meta data for %s songs", len(tag_meta))

        with self._database.scoped_session(read_only=False) as session:
            self._clean_existing_tags(session)
            self._insert_new_tags(session, tag_meta)
