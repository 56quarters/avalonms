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


"""Main entry point for collection scanning and HTTP server."""

import pkgutil
import threading
from datetime import datetime

import cherrypy

import avalon.cache
import avalon.exc
import avalon.ids
import avalon.log
import avalon.models
import avalon.server
import avalon.tags.insert
import avalon.tags.read
import avalon.tags.scan
import avalon.web.api
import avalon.web.handler
import avalon.web.filtering
import avalon.web.search


APP_PATH = '/avalon'


def setup_cherrypy_env():
    """ """
    cherrypy.config.update({'environment': 'production'})
    cherrypy.log.access_file = None
    cherrypy.log.error_file = None
    cherrypy.log.screen = False


def new_logger(app_config, logger_root):
    """ """
    log_config = avalon.log.AvalonLogConfig()
    log_config.log_root = logger_root
    log_config.access_path = app_config.access_log
    log_config.error_path = app_config.error_log
    return avalon.log.AvalonLog(log_config)


def new_db_engine(app_config, logger):
    """ """
    url = 'sqlite:///%s' % app_config.db_path
    db_config = avalon.models.SessionHandlerConfig()
    db_config.engine = avalon.models.get_engine(url)
    db_config.session_factory = avalon.models.get_session_factory()
    db_config.metadata = avalon.models.get_metadata()
    db_config.log = logger
    return avalon.models.SessionHandler(db_config)


def new_handler(db_engine):
    """ """
    api_config = avalon.web.api.AvalonApiEndpointsConfig()
    api_config.track_store = avalon.cache.TrackStore(db_engine)
    api_config.album_store = avalon.cache.AlbumStore(db_engine)
    api_config.artist_store = avalon.cache.ArtistStore(db_engine)
    api_config.genre_store = avalon.cache.GenreStore(db_engine)
    api_config.id_cache = avalon.cache.IdLookupCache(db_engine)

    api_config.search = avalon.web.search.AvalonTextSearch(
        api_config.album_store,
        api_config.artist_store,
        api_config.genre_store,
        api_config.track_store)

    api = avalon.web.api.AvalonApiEndpoints(api_config)

    # Configure the status endpoints including loading an HTML template
    status_config = avalon.web.api.AvalonStatusEndpointsConfig()
    status_config.ready = threading.Event()
    status_config.status_tpt = pkgutil.get_data('avalon.web', 'data/status.html')
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

