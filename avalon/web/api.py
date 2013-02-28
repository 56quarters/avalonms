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


"""API endpoints for the in-memory stores."""

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
    """Endpoints for querying in-memory stores of audio metadata."""

    def __init__(self, config):
        """Set each of the in-memory stores to be used."""
        self._tracks = config.track_store
        self._albums = config.album_store
        self._artists = config.artist_store
        self._genres = config.genre_store
        self._search = config.search
        self._id_cache = config.id_cache

    def reload(self):
        """Reload in-memory stores from the database."""
        self._tracks.reload()
        self._albums.reload()
        self._artists.reload()
        self._genres.reload()
        self._search.reload()
        self._id_cache.reload()

    def get_search_size(self):
        """Get the number of nodes in the search index."""
        return self._search.size()

    def get_albums(self, params=None):
        """Return album results based on the given query string
        parameters, all albums if there are no parameters.
        """
        all_albums = self._albums.all()
        if params is None or params.get('query') is None:
            return all_albums
        return self._search.search_albums(params.get('query'))

    def get_artists(self, params=None):
        """Return artist results based on the given query string
        parameters, all artists if there are no parameters.
        """
        all_artists = self._artists.all()
        if params is None or params.get('query') is None:
            return all_artists
        return self._search.search_artists(params.get('query'))

    def get_genres(self, params=None):
        """Return genre results based on the given query string
        parameters, all genres if there are no parameters.
        """
        all_genres = self._genres.all()
        if params is None or params.get('query') is None:
            return all_genres
        return self._search.search_genres(params.get('query'))

    def get_songs(self, params=None):
        """Return song results based on the given query string
        parameters, all songs if there are no parameters."""
        if params is None:
            return self._tracks.all()

        sets = []

        if params.get('query') is not None:
            sets.append(
                self._search.search_tracks(params.get('query')))
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

        album_id = params.get_uuid('album_id')
        artist_id = params.get_uuid('artist_id')
        genre_id = params.get_uuid('genre_id')

        if album_id is not None:
            sets.append(self._tracks.by_album(album_id))
        if artist_id is not None:
            sets.append(self._tracks.by_artist(artist_id))
        if genre_id is not None:
            sets.append(self._tracks.by_genre(genre_id))

        if sets:
            # Return the intersection of any non-None sets
            return intersection(sets)
            # There were no parameters to filter songs by any criteria
        return self._tracks.all()


class AvalonStatusEndpointsConfig(object):
    """Configuration for the status endpoints."""

    def __init__(self):
        self.ready = None


class AvalonStatusEndpoints(object):
    """Status endpoints for information about the running application."""

    def __init__(self, config):
        """Initialize the ready state of the server."""
        self._ready = config.ready

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

    def get_server_data(self, startup, api):
        """Get a dictionary of various bits of data about the currently
        running server.

        Keys include: status, user, group, uptime, memory, threads,
        albums, artists, genres, tracks, and trie_nodes.
        """
        return {
            'status': 'ready' if self.ready else 'not-ready',
            'user': avalon.util.get_current_uname(),
            'group': avalon.util.get_current_gname(),
            'uptime': str(datetime.utcnow() - startup),
            'memory': avalon.util.get_mem_usage(),
            'threads': avalon.util.get_thread_names(),
            'albums': len(api.get_albums()),
            'artists': len(api.get_artists()),
            'genres': len(api.get_genres()),
            'tracks': len(api.get_songs()),
            'trie_nodes': api.get_search_size()
        }

    def get_heartbeat(self):
        """Get the heartbeat to indicate if the server has started."""
        if self.ready:
            return "OKOKOK"
        return "NONONO"

