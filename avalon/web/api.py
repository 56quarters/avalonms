# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


"""API endpoints for the in-memory meta data stores."""

from datetime import datetime
import functools

import avalon.util


__all__ = [
    'intersection',
    'AvalonApiEndpoints',
    'AvalonApiEndpointsConfig',
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
    """Configuration for the metadata endpoints.

    Expected configuration values include in-memory stores for
    all tracks, albums, artists, and genres, A structure that
    supports text matching for each of those types, and a way
    translate names to IDs and vice versa.
    """

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

    def get_albums(self, params=None):
        """Return album results based on the given query string
        parameters, all albums if there are no parameters.
        """
        all_albums = self._albums.get_all()
        if params is None or params.get('query') is None:
            return all_albums
        return self._search.search_albums(params.get('query'))

    def get_artists(self, params=None):
        """Return artist results based on the given query string
        parameters, all artists if there are no parameters.
        """
        all_artists = self._artists.get_all()
        if params is None or params.get('query') is None:
            return all_artists
        return self._search.search_artists(params.get('query'))

    def get_genres(self, params=None):
        """Return genre results based on the given query string
        parameters, all genres if there are no parameters.
        """
        all_genres = self._genres.get_all()
        if params is None or params.get('query') is None:
            return all_genres
        return self._search.search_genres(params.get('query'))

    def get_songs(self, params=None):
        """Return song results based on the given query string
        parameters, all songs if there are no parameters."""
        if params is None:
            return self._tracks.get_all()

        sets = []

        if params.get('query') is not None:
            sets.append(
                self._search.search_tracks(params.get('query')))
        if params.get('album') is not None:
            sets.append(
                self._tracks.get_by_album(
                    self._id_cache.get_album_id(params.get('album'))))
        if params.get('artist') is not None:
            sets.append(
                self._tracks.get_by_artist(
                    self._id_cache.get_artist_id(params.get('artist'))))
        if params.get('genre') is not None:
            sets.append(
                self._tracks.get_by_genre(
                    self._id_cache.get_genre_id(params.get('genre'))))

        album_id = params.get_uuid('album_id')
        artist_id = params.get_uuid('artist_id')
        genre_id = params.get_uuid('genre_id')

        if album_id is not None:
            sets.append(self._tracks.get_by_album(album_id))
        if artist_id is not None:
            sets.append(self._tracks.get_by_artist(artist_id))
        if genre_id is not None:
            sets.append(self._tracks.get_by_genre(genre_id))

        if sets:
            # Return the intersection of any non-None sets
            return intersection(sets)

        # There were no parameters to filter songs by any criteria
        return self._tracks.get_all()


class AvalonStatusEndpointsConfig(object):
    """Configuration for the status endpoints.

    Expected configuration values include a threading.Event to
    be used to mark the server as up or down and the datetime of
    server startup in UTC.
    """

    def __init__(self):
        self.ready = None
        self.startup = None


class AvalonStatusEndpoints(object):
    """Status endpoints for information about the running application."""

    def __init__(self, config):
        """Initialize the ready state of the server."""
        self._ready = config.ready
        self._startup = config.startup

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

    def get_uptime(self):
        """Get a timedelta object for the uptime of the current server."""
        return datetime.utcnow() - self._startup

    def get_threads(self):
        """Get a list of the names of each thread currently running."""
        return avalon.util.get_thread_names()

    def get_memory_usage(self):
        """Get the current memory usage in MB"""
        return avalon.util.get_mem_usage()

    def get_heartbeat(self):
        """Get the heartbeat to indicate if the server has started."""
        if self.ready:
            return "OKOKOK"
        return "NONONO"

