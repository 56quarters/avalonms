# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2013 TSH Labs <projects@tshlabs.org>
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


"""Factory methods for the major components of the music server."""

import threading
from datetime import datetime

from cherrypy._cptree import Application as CherryPyApplication

import avalon.app.plugins
import avalon.cache
import avalon.log
import avalon.models
import avalon.server
import avalon.util
import avalon.web.api
import avalon.web.handler
import avalon.web.filtering
import avalon.web.search


__all__ = [
    'new_logger',
    'new_db_engine',
    'new_dao',
    'new_handler',
    'new_server',
    'new_plugin_engine'
]


def new_logger(app_config, logger_root):
    """Construct a new logger based on the given configuration
    and root logger.

    Expected configuration properties are: access_log and
    error_log.
    """
    log_config = avalon.log.AvalonLogConfig()
    log_config.log_root = logger_root
    log_config.access_path = app_config.access_log
    log_config.error_path = app_config.error_log
    return avalon.log.AvalonLog(log_config)


def new_db_engine(app_config, logger):
    """Construct a new database handler with an SQLite backend
    based on the given configuration and logger.

    Expected configuration properties are: db_path.
    """
    url = 'sqlite:///%s' % app_config.db_path
    db_config = avalon.models.SessionHandlerConfig()
    db_config.engine = avalon.models.get_engine(url)
    db_config.session_factory = avalon.models.get_session_factory()
    db_config.metadata = avalon.models.get_metadata()
    db_config.log = logger
    return avalon.models.SessionHandler(db_config)


def new_dao(db_engine):
    """Construct a new read-only DAO from the given :class:`SessionHandler`"""
    return avalon.cache.ReadOnlyDao(db_engine)


def new_handler(dao):
    """Construct a new web request handler using the given DAO"""
    api_config = avalon.web.api.AvalonApiEndpointsConfig()
    api_config.track_store = avalon.cache.TrackStore(dao)
    api_config.album_store = avalon.cache.AlbumStore(dao)
    api_config.artist_store = avalon.cache.ArtistStore(dao)
    api_config.genre_store = avalon.cache.GenreStore(dao)
    api_config.id_cache = avalon.cache.IdLookupCache(dao)

    def trie_factory():
        return avalon.web.search.SearchTrie(avalon.web.search.TrieNode)

    api_config.search = avalon.web.search.AvalonTextSearch(
        api_config.album_store,
        api_config.artist_store,
        api_config.genre_store,
        api_config.track_store,
        trie_factory)

    api = avalon.web.api.AvalonApiEndpoints(api_config)

    status_config = avalon.web.api.AvalonStatusEndpointsConfig()
    status_config.ready = threading.Event()
    status = avalon.web.api.AvalonStatusEndpoints(status_config)

    filters = [
        # NOTE: Sort needs to come before limit
        avalon.web.filtering.sort_filter,
        avalon.web.filtering.limit_filter]

    startup = datetime.utcnow()

    handler_config = avalon.web.handler.AvalonHandlerConfig()
    handler_config.api_endpoints = api
    handler_config.status_endpoints = status
    handler_config.filters = filters
    handler_config.startup = startup

    return avalon.web.handler.AvalonHandler(handler_config)


def new_server(app_config, logger, handler, path):
    """Construct a new HTTP server using the given configuration,
    logger, request handler, and desired application path.

    Expected configuration properties are: server_address,
    server_port, server_threads, and server_queue.
    """
    server_config = avalon.server.AvalonServerConfig()
    server_config.log = logger
    server_config.bind_addr = (
        app_config.server_address,
        app_config.server_port)
    server_config.num_threads = app_config.server_threads
    server_config.queue_size = app_config.server_queue
    server_config.application = CherryPyApplication(handler, script_name=path)
    return avalon.server.AvalonServer(server_config)


def new_plugin_engine(app_config, logger, db_engine, server, bus):
    """Construct a new plugin engine/manager from the given logger,
    database handler, HTTP server, and message bus.

    Expected configuration properties are: daemon, daemon_user,
    daemon_group, access_log, error_log, db_path, collection.
    """
    engine_config = avalon.app.plugins.PluginEngineConfig()
    engine_config.log = logger
    engine_config.db = db_engine
    engine_config.server = server
    engine_config.bus = bus

    engine = avalon.app.plugins.PluginEngine(engine_config)

    if app_config.daemon:
        engine.enable_daemon(
            avalon.util.get_uid(app_config.daemon_user),
            avalon.util.get_gid(app_config.daemon_group),
            set([
                app_config.access_log,
                app_config.error_log,
                app_config.db_path]))

    if not app_config.no_scan:
        engine.enable_scan(app_config.collection)

    return engine

