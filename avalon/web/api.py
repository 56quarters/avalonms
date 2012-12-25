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


"""API endpoints for the in memory stores."""


import functools
from datetime import datetime

import avalon.util


__all__ = [
    'intersection',
    'AvalonApiEndpoints',
    'AvalonApiEndpointsConfig'
    'AvalonStatusEndpoints',
    'AvalonStatusEndpointsConfig'
    ]


def intersection(sets):
    """Find the intersection of all of the given non-None sets."""
    # NOTE: we use 'not None' here instead of a simple boolean test
    # because we want the intersection with an empty set to actually
    # mean 'there were 0 results'.
    return functools.reduce(
        lambda x, y: x.intersection(y),
        [res_set for res_set in sets if res_set is not None])


class AvalonApiEndpointsConfig(object):

    """Configuration for the metadata endpoints."""

    def __init__(self):
        self.track_store = None
        self.album_store = None
        self.artist_store = None
        self.genre_store = None
        self.search = None
        self.id_cache = None


class AvalonApiEndpoints(object):

    """Endpoints for querying in memory stores of audio metadata."""

    def __init__(self, config):
        """Initialize each of the stores by loading from the database."""
        self._tracks = config.track_store
        self._albums = config.album_store
        self._artists = config.artist_store
        self._genres = config.genre_store
        self._search = config.search
        self._id_cache = config.id_cache

    def reload(self):
        """Reload in memory stores from the database."""
        self._tracks.reload()
        self._albums.reload()
        self._artists.reload()
        self._genres.reload()
        self._id_cache.reload()

    def get_albums(self, params=None):
        """ """
        all_albums = self._albums.all()
        if params is None or params.get('query') is None:
            return all_albums
        return self._search.search_basic(all_albums, params.get('query'))

    def get_artists(self, params=None):
        """ """
        all_artists = self._artists.all()
        if params is None or params.get('query') is None:
            return all_artists
        return self._search.search_basic(all_artists, params.get('query'))

    def get_genres(self, params=None):
        """ """
        all_genres = self._genres.all()
        if params is None or params.get('query') is None:
            return all_genres
        return self._search.search_basic(all_genres, params.get('query'))

    def get_songs(self, params=None):
        """Return song results based on the given query string
        parameters, all songs if there are no parameters."""
        if params is None:
            return self._tracks.all()

        sets = []
        if params.get('album') is not None:
            sets.append(
                self._tracks.by_album(
                    self._id_cache.get_album_id(params.get('album'))))
        if params.get('artist') is not None:
            sets.append(
                self._tracks.by_artist(
                    self._id_cache.get_artist_id(params.get('artist'))))
        if params.get('genre') is not None:
            sets.append(
                self._tracks.by_genre(
                    self._id_cache.get_genre_id(params.get('genre'))))

        if params.get('album_id') is not None:
            sets.append(self._tracks.by_album(params.get('album_id')))
        if params.get('artist_id') is not None:
            sets.append(self._tracks.by_artist(params.get('artist_id')))
        if params.get('genre_id') is not None:
            sets.append(self._tracks.by_genre(params.get('genre_id')))
            
        if sets:
            # Return the intersection of any non-None sets
            return intersection(sets)
        # There were no parameters to filter songs by any criteria
        return self._tracks.all()


class AvalonStatusEndpointsConfig(object):

    """Configuration for the status endpoints."""

    def __init__(self):
        self.ready = None
        self.status_tpt = None


class AvalonStatusEndpoints(object):

    """Status endpoints for information about the running application."""

    def __init__(self, config):
        """Initialize the ready state of the server."""
        self._ready = config.ready
        self._status_tpt = config.status_tpt

    def _get_ready(self):
        """Get the ready state of the application."""
        return self._ready.is_set()

    def _set_ready(self, val):
        """Set the ready state of the application."""
        if val:
            self._ready.set()
        else:
            self._ready.clear()

    ready = property(
        _get_ready, _set_ready, None, "Is the application ready")

    def reload(self):
        """No-op."""
        pass

    def get_status_page(self, startup, api):
        """Get an HTML status page interpolated with values from the
        running server.
        """
        return self._status_tpt % {
            'status': 'ready' if self.ready else 'not ready',
            'user': avalon.util.get_current_uname(),
            'group': avalon.util.get_current_gname(),
            'uptime': datetime.utcnow() - startup,
            'memory': avalon.util.get_mem_usage(),
            'threads': '<br />'.join(avalon.util.get_thread_names()),
            'albums': len(api.get_albums()),
            'artists': len(api.get_artists()),
            'genres': len(api.get_genres()),
            'tracks': len(api.get_songs())
            }

    def get_heartbeat(self):
        """Get the heartbeat to indicate if the server has started."""
        if self.ready:
            return "OKOKOK"
        return "NONONO"

