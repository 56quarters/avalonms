#!/usr/bin/env python
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

import threading
import pkgutil
from datetime import datetime

import cherrypy

import avalon.cache
import avalon.log
import avalon.models
import avalon.web.handler
import avalon.web.api
import avalon.web.filtering
import avalon.web.search


class AvalonHandlerFactoryConfig(object):

    def __init__(self):
        self.db_path = None
        self.access_log = None
        self.error_log = None


class AvalonHandlerFactory(object):

    def __init__(self, config):
        self._config = config
        self._log = None
        self._db = None
        self._app = None
        self._setup()

    def get_db(self):
        return self._db

    def get_log(self):
        return self._log

    def get_handler(self):
        return self._app

    def _setup(self):
        self._log = self._build_logger()
        self._db = self._build_db_engine()
        self._db.connect()
        self._app = self._build_handler()

    def _build_logger(self):
        """Configure and return the application logger."""
        config = avalon.log.AvalonLogConfig()
        config.log_root = cherrypy.log
        config.access_path = self._config.access_log
        config.error_path = self._config.error_log
        return avalon.log.AvalonLog(config)

    def _build_db_engine(self):
        """Configure and return the database handler."""
        url = 'sqlite:///%s' % self._config.db_path
        config = avalon.models.SessionHandlerConfig()
        config.engine = avalon.models.get_engine(url)
        config.session_factory = avalon.models.get_session_factory()
        config.metadata = avalon.models.get_metadata()
        config.log = self._log

        return avalon.models.SessionHandler(config)

    def _build_handler(self):
        """Configure and return the web request handler."""
        api_config = avalon.web.api.AvalonApiEndpointsConfig()
        api_config.track_store = avalon.cache.TrackStore(self._db)
        api_config.album_store = avalon.cache.AlbumStore(self._db)
        api_config.artist_store = avalon.cache.ArtistStore(self._db)
        api_config.genre_store = avalon.cache.GenreStore(self._db)
        api_config.id_cache = avalon.cache.IdLookupCache(self._db)

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

        config = avalon.web.handler.AvalonHandlerConfig()
        config.api_endpoints = api
        config.status_endpoints = status
        config.filters = filters
        config.startup = startup

        return avalon.web.handler.AvalonHandler(config)


def default_settings():
    config = AvalonHandlerFactoryConfig()
    config.db_path = '/tmp/avalon.sqlite'
    config.access_log = '/tmp/avalon.log'
    config.error_log = '/tmp/avalon.err'
    return config


def new_handler():
    config = default_settings()
    factory = AvalonHandlerFactory(config)
    handler = factory.get_handler()
    handler.ready = True

    return cherrypy.tree.mount(handler, script_name='/avalon')


application = new_handler()

