# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Scan the music collection and insert metadata into the database."""

from __future__ import absolute_import, unicode_literals

import argparse
import logging
import sys

import os.path
import avalon
import avalon.app.factory
import avalon.compat
import avalon.exc
import avalon.ids
import avalon.log
import avalon.tags.crawl
import avalon.tags.insert
import avalon.tags.read
from avalon.app.bootstrap import build_config, CONFIG_ENV_VAR
from avalon.cli import install_sigint_handler
from avalon.models import Album, Artist, Genre, Track


class AvalonCollectionScanner(object):
    """High-level logic for reading metadata from a music collection
    and inserting it into a SQL database of some sort.
    """
    _logger = avalon.log.get_error_log()

    def __init__(self, database, id_cache):
        """Set the database connection manager and ID-lookup cache
        to use for scanning the music collection.

        :param avalon.models.SessionHandler database: Database session
            handler to use for inserting metadata into a database.
        :param avalon.cache.IdLookupCache id_cache: In-memory store for
            looking up IDs of albums, artists, and genres based on their
            name.
        """
        self._database = database
        self._id_cache = id_cache

    def _clean_existing_tags(self, session):
        """Remove all existing metadata from the database using the
        given session.

        The session is expected to be using a transaction that will allow
        the deletion of existing data to be rolled back if needed.

        :param sqlalchemy.orm.Session session: Session to use for removing
            all existing meta ata from the database.
        """
        self._logger.info("Removing old metadata...")
        cleaner = avalon.tags.insert.Cleaner(session)
        for cls in (Album, Artist, Genre, Track):
            cleaner.clean_type(cls)

    def _insert_new_tags(self, session, tag_meta):
        """Insert new entries into the album, artist, genre, and track
        tables based on the given audio tag metadata.

        The session is expected to be using a transaction that will allow
        the insertion of data to be rolled back if needed.

        :param sqlalchemy.orm.Session session: Session to use for inserting
            new metadata into the database.
        :param list tag_meta: List of :class:`avalon.tags.read.Metadata` instances
            resulting from reading audio metadata from a music collection.
        """
        self._logger.info("Inserting new tag metadata for associated attributes...")
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

        self._logger.info("Inserting new tag metadata for songs...")
        track_loader = avalon.tags.insert.TrackLoader(session, tag_meta, self._id_cache)
        track_loader.insert(Track, avalon.ids.get_track_id)

    def scan_path(self, path):
        """Recursively scan the given path for files, attempt to read audio
        metadata from them, and insert the resulting metadata into a
        database of some sort.

        Deletion of existing metadata and insertion of new metadata is
        done within the context of a transaction such that the database
        will be left in a consistent state.

        :param str path: Relative or absolute path to a music collection
        """
        self._logger.info(
            "Crawling music collection at %s...", path)

        crawler = avalon.app.factory.new_crawler(path)
        tag_meta = crawler.get_tags()

        self._logger.info("Loaded metadata for %s songs", len(tag_meta))

        with self._database.scoped_session(read_only=False) as session:
            self._clean_existing_tags(session)
            self._insert_new_tags(session, tag_meta)


def get_opts(prog):
    parser = argparse.ArgumentParser(
        prog=prog,
        description=__doc__)

    parser.add_argument(
        'collection',
        help='Path to the root of your music collection')

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=avalon.__version__,
        help='Show the version of the Avalon Music Server and exit')

    parser.add_argument(
        '-d',
        '--database-url',
        metavar='URL',
        help='Database URL connection string for the database to '
             'write music collection metadata to. If not specified '
             'the value from the default configuration file and '
             'configuration file override will be used. The URL must '
             'be one supported by SQLAlchemy. See documentation '
             'here: http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls')

    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Be less verbose, only emit ERROR level messages to the '
             'console')

    return parser.parse_args()


def main():
    install_sigint_handler()
    prog = os.path.basename(sys.argv[0])
    args = get_opts(prog)
    config = build_config(env_var=CONFIG_ENV_VAR)

    if args.database_url:
        config['DATABASE_URL'] = avalon.cli.input_to_text(args.database_url)

    if args.quiet:
        config['LOG_LEVEL'] = logging.ERROR

    logger = avalon.log.get_error_log()
    avalon.app.factory.configure_logger(logger, config)

    try:
        database = avalon.app.factory.new_db_engine(config)
        database.connect()
    except avalon.exc.DatabaseError as e:
        logger.error("%s: %s", prog, e)
        return 1

    dao = avalon.app.factory.new_dao(database)
    id_cache = avalon.app.factory.new_id_cache(dao)
    scanner = AvalonCollectionScanner(database, id_cache)
    collection = avalon.cli.input_to_text(args.collection)

    try:
        scanner.scan_path(collection)
    except avalon.exc.AvalonError as e:
        logger.error(
            "%s: Scanning of music collection at %s failed: %s",
            prog, args.collection, e)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
