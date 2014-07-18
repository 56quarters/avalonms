# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Factory methods for the major components of the music server."""

from __future__ import unicode_literals

from datetime import datetime

import re
import mutagenx
import avalon.cache
import avalon.log
import avalon.models
import avalon.tags.insert
import avalon.tags.read
import avalon.tags.crawl
import avalon.util
import avalon.web.api
import avalon.web.controller
import avalon.web.filtering
import avalon.web.search


__all__ = [
    'configure_logger',
    'new_controller',
    'new_dao',
    'new_db_engine',
    'new_crawler',
    'new_id_cache'
]


def configure_logger(logger, config):
    """Configure the server-wide logger for the Avalon Music Server based
    on the given configuration, making sure to only add handlers to the logger,
    not removing any existing ones.

    :param logging.Logger logger: Logger instance to configure
    :param flask.Config config: Application level configuration
    :return: Global logger for the Avalon Music Server
    :rtype: logging.Logger
    """
    log_config = avalon.log.AvalonLogConfig()
    log_config.path = config.get('LOG_PATH')
    log_config.level = config.get('LOG_LEVEL')
    log_config.fmt = config.get('LOG_FORMAT')
    log_config.date_fmt = config.get('LOG_DATE_FORMAT')
    avalon.log.initialize(logger, log_config)
    return avalon.log.get_error_log()


def new_db_engine(config):
    """Construct a new database handler with an SQLite backend based on the
    given configuration and logger.

    Expected configuration properties are: db_path.

    :param flask.Config config: Application level configuration
    :return: Handler for managing database sessions
    :rtype: avalon.models.SessionHandler
    """
    url = config.get('DATABASE_URL')
    db_config = avalon.models.SessionHandlerConfig()
    db_config.engine = avalon.models.get_engine(url)
    db_config.session_factory = avalon.models.get_session_factory()
    db_config.metadata = avalon.models.get_metadata()

    return avalon.models.SessionHandler(db_config)


def new_crawler(path):
    """Construct a new tag crawler capable finding all audio files
    under a given path and reading their audio meta data.

    Files that to not have valid audio meta data will be ignored and
    the error will be logged.

    :param str path: Root path of the music collection to crawl
    :return: New tag crawler to read all audio meta data under the root
    :rtype: avalon.tags.crawl.TagCrawler
    """
    track_parser = avalon.tags.read.MetadataTrackParser(re.match)
    date_parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
    loader = avalon.tags.read.MetadataLoader(
        mutagenx,
        track_parser,
        date_parser)

    return avalon.tags.crawl.TagCrawler(loader, path)


def new_dao(db_engine):
    """Construct a new read-only DAO from the given :class:`SessionHandler`.

    :param avalon.models.SessionHandler db_engine: Database session manager
    :return: Simple facade over the database session manager
    :rtype: avalon.models.ReadOnlyDao
    """
    return avalon.models.ReadOnlyDao(db_engine)


def new_id_cache(dao):
    """Construct a new ID-to-name store based on the given read-only DAO.

    :param avalon.cache.ReadOnlyDao dao: Read-only DAO for loading ID-name
        mappings
    :return: ID-name lookup cache
    :rtype: avalon.cache.IdLookupCache
    """
    return avalon.cache.IdLookupCache(dao)


def new_controller(dao, id_cache):
    """Construct a new web request handler using the given DAO.

    :param avalon.cache.ReadOnlyDao dao: Read-only DAO for various
        music meta data stores that will be loaded
    :param avalon.cache.IdLookupCache id_cache: ID-name cache used
        by the request handler for translating by-name requests into
        ID based lookups
    :return: Service to be use as web endpoints or a controller
    :rtype: avalon.web.controller.AvalonController
    """
    api_config = avalon.web.api.AvalonApiEndpointsConfig()
    api_config.track_store = avalon.cache.TrackStore(dao)
    api_config.album_store = avalon.cache.AlbumStore(dao)
    api_config.artist_store = avalon.cache.ArtistStore(dao)
    api_config.genre_store = avalon.cache.GenreStore(dao)
    api_config.id_cache = id_cache

    def trie_factory():
        return avalon.web.search.SearchTrie(avalon.web.search.TrieNode)

    api_config.search = avalon.web.search.AvalonTextSearch(
        api_config.album_store,
        api_config.artist_store,
        api_config.genre_store,
        api_config.track_store,
        trie_factory)

    api = avalon.web.api.AvalonApiEndpoints(api_config)

    filters = [
        # NOTE: Sort needs to come before limit
        avalon.web.filtering.sort_filter,
        avalon.web.filtering.limit_filter]

    controller_config = avalon.web.controller.AvalonControllerConfig()
    controller_config.api_endpoints = api
    controller_config.filters = filters

    return avalon.web.controller.AvalonController(controller_config)
