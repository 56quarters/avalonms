# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Factory methods for the major components of the music server."""

from __future__ import absolute_import, unicode_literals

import logging
from datetime import datetime

import re
import mutagen
import avalon.cache
import avalon.log
import avalon.models
import avalon.tags.insert
import avalon.tags.read
import avalon.tags.crawl
import avalon.util
import avalon.web.services
import avalon.web.controller
import avalon.web.filtering
import avalon.web.search


def configure_logger(logger, config):
    """Configure the server-wide logger for the Avalon Music Server based
    on the given configuration, making sure to only add handlers to the logger,
    not removing any existing ones.

    :param logging.Logger logger: Logger instance to configure
    :param flask.Config config: Application level configuration
    """
    log_config = avalon.log.AvalonLogConfig()
    log_config.path = config.get('LOG_PATH')
    log_config.level = config.get('LOG_LEVEL')
    log_config.fmt = config.get('LOG_FORMAT')
    log_config.date_fmt = config.get('LOG_DATE_FORMAT')
    avalon.log.initialize(logger, log_config)


def configure_sentry_logger(logger, config):
    """Configure a Sentry client for messages logged at ERROR and higher.

    If a Sentry client is not installed or has not been configured, a handler
    will not be installed. See the Sentry_ docs for more information.

    .. _Sentry https://www.getsentry.com/docs/

    :param logging.Logger logger: Flask application logger
    :param flask.Config config: Application configuration
    """
    try:
        from raven.handlers.logging import SentryHandler
        from raven.conf import setup_logging

        handler = SentryHandler(config['SENTRY_DSN'], level=logging.ERROR)
        setup_logging(handler)
    except ImportError:
        logger.info("Sentry client not installed, skipping setup")
    except (ValueError, KeyError):
        logger.info("Sentry not configured, skipping setup")
    else:
        logger.info("Sentry client configured for ERROR messages")


def new_stats_client(logger, config):
    """Configure a stats client for recording metric counts or timings.

    If a stats client is not installed ``None`` will be returned. By
    default the stats client will write metrics to localhost on port
    8125. Since it uses UDP, if there is no server running these will
    just be ignored.

    See https://github.com/etsy/statsd/ or https://github.com/jsocol/pystatsd
    for more information.

    :param logging.Logger logger: Flask application logger
    :param flask.Config config: Application configuration
    :return: Configured stats client or None
    :rtype: statsd.StatsClient
    """
    try:
        import statsd
    except ImportError:
        logger.info("Statsd client not installed, skipping setup")
        return None

    logger.info("Statsd client configured for request timing")
    return statsd.StatsClient(
        host=config['STATSD_HOST'],
        port=config['STATSD_PORT'],
        prefix=config['STATSD_PREFIX'])


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
    under a given path and reading their audio metadata.

    Files that to not have valid audio metadata will be ignored and
    the error will be logged.

    :param str path: Root path of the music collection to crawl
    :return: New tag crawler to read all audio metadata under the root
    :rtype: avalon.tags.crawl.TagCrawler
    """
    track_parser = avalon.tags.read.MetadataTrackParser(re.match)
    date_parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
    loader = avalon.tags.read.MetadataLoader(
        mutagen,
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
        music metadata stores that will be loaded
    :param avalon.cache.IdLookupCache id_cache: ID-name cache used
        by the request handler for translating by-name requests into
        ID based lookups
    :return: Controller to be used as web API endpoints
    :rtype: avalon.web.controller.AvalonController
    """
    service_config = avalon.web.services.AvalonMetadataServiceConfig()
    service_config.track_store = avalon.cache.TrackStore(dao)
    service_config.album_store = avalon.cache.AlbumStore(dao)
    service_config.artist_store = avalon.cache.ArtistStore(dao)
    service_config.genre_store = avalon.cache.GenreStore(dao)
    service_config.id_cache = id_cache

    # pylint: disable=missing-docstring
    def trie_factory():
        return avalon.web.search.SearchTrie(avalon.web.search.TrieNode)

    service_config.search = avalon.web.search.AvalonTextSearch(
        service_config.album_store,
        service_config.artist_store,
        service_config.genre_store,
        service_config.track_store,
        trie_factory)

    service = avalon.web.services.AvalonMetadataService(service_config)

    filters = [
        # NOTE: Sort needs to come before limit
        avalon.web.filtering.sort_filter,
        avalon.web.filtering.limit_filter]

    controller_config = avalon.web.controller.AvalonControllerConfig()
    controller_config.api_endpoints = service
    controller_config.filters = filters

    return avalon.web.controller.AvalonController(controller_config)
