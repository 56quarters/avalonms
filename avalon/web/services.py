# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""API endpoints for the in-memory meta data stores."""

from __future__ import unicode_literals
import functools

import avalon.log


__all__ = [
    'intersection',
    'AvalonMetadataService',
    'AvalonMetadataServiceConfig'
]

# Disable warning about constant that's really a function
# pylint: disable=invalid-name
_set_intersection = lambda x, y: x.intersection(y)


def intersection(sets):
    """Find the intersection of all of the given non-None sets."""
    # NOTE: we use 'not None' here instead of a simple boolean test
    # because we want the intersection with an empty set to actually
    # mean 'there were 0 results'.
    return functools.reduce(
        _set_intersection,
        [res_set for res_set in sets if res_set is not None])


class AvalonMetadataServiceConfig(object):
    """Configuration for the metadata endpoints.

    :ivar avalon.cache.TrackStore track_store: In-memory store for
        looking up tracks by various attributes
    :ivar avalon.cache.AlbumStore album_store: In-memory store for
        looking up albums by various attributes
    :ivar avalon.cache.ArtistStore artist_store: In-memory store for
        looking up artists by various attributes
    :ivar avalon.cache.GenreStore genre_store: In-memory store for
        looking up genres by various attributes
    :ivar avalon.web.search.AvalonTextSearch search: In-memory store
        for doing text matching of tracks, albums, artists, and genres
        by their names or various attributes.
    :ivar avalon.cache.IdNameStore id_cache: In-memory store for
        looking up the UUID of tracks, albums, artists, or genres
        by their name.
    """

    def __init__(self):
        self.track_store = None
        self.album_store = None
        self.artist_store = None
        self.genre_store = None
        self.search = None
        self.id_cache = None


class AvalonMetadataService(object):
    """Methods for querying in-memory stores of audio metadata."""

    _logger = avalon.log.get_error_log()

    def __init__(self, config):
        """Set each of the in-memory stores to be used."""
        self._tracks = config.track_store
        self._albums = config.album_store
        self._artists = config.artist_store
        self._genres = config.genre_store
        self._search = config.search
        self._id_cache = config.id_cache

    def reload(self):
        """Reload in-memory stores from the database.

        :return: This object
        :rtype: AvalonApiEndpoints
        """
        self._tracks.reload()
        self._albums.reload()
        self._artists.reload()
        self._genres.reload()
        self._search.reload()
        self._id_cache.reload()

        self._logger.info('Loaded %s tracks', len(self._tracks))
        self._logger.info('Loaded %s albums', len(self._albums))
        self._logger.info('Loaded %s artists', len(self._artists))
        self._logger.info('Loaded %s genres', len(self._genres))
        self._logger.info('Using %s trie nodes', len(self._search))

        return self

    def get_albums(self, params=None):
        """Return album results based on the given query string
        parameters, all albums if there are no parameters.

        Supported parameters are:

        * ``query`` -- Search term

        :param avalon.web.request.Parameters params: Request parameters
            to filter albums by or None
        :return: All albums that match the given parameters
        :rtype: frozenset
        """
        if params is None or params.get('query') is None:
            return self._albums.get_all()
        return self._search.search_albums(params.get('query'))

    def get_artists(self, params=None):
        """Return artist results based on the given query string
        parameters, all artists if there are no parameters.

        Supported parameters are:

        * ``query`` -- Search term

        :param avalon.web.request.Parameters params: Request parameters
            to filter artists by or None
        :return: All albums that match the given parameters
        :rtype: frozenset
        """
        if params is None or params.get('query') is None:
            return self._artists.get_all()
        return self._search.search_artists(params.get('query'))

    def get_genres(self, params=None):
        """Return genre results based on the given query string
        parameters, all genres if there are no parameters.

        Supported parameters are:

        * ``query`` -- Search term

        :param avalon.web.request.Parameters params: Request parameters
            to filter genres by or None
        :return: All genres that match the given parameters
        :rtype: frozenset
        """
        if params is None or params.get('query') is None:
            return self._genres.get_all()
        return self._search.search_genres(params.get('query'))

    def get_songs(self, params=None):
        """Return song results based on the given query string
        parameters, all songs if there are no parameters.

        Supported parameters are:

        * ``query`` -- Search term
        * ``album`` -- Album name
        * ``artist`` -- Artist name
        * ``genre`` -- Genre name
        * ``album_id`` -- Album UUID
        * ``artist_id`` -- Artist UUID
        * ``genre_id`` -- Genre UUID

        :param avalon.web.request.Parameters params: Request parameters
            to filter tracks by or None
        :return: All tracks that match the given parameters
        :rtype: frozenset
        """
        if params is None:
            return self._tracks.get_all()

        sets = []
        query = params.get('query')
        album = params.get('album')
        artist = params.get('artist')
        genre = params.get('genre')
        album_id = params.get_uuid('album_id')
        artist_id = params.get_uuid('artist_id')
        genre_id = params.get_uuid('genre_id')

        if query is not None:
            sets.append(
                self._search.search_tracks(query))
        if album is not None:
            sets.append(
                self._tracks.get_by_album(
                    self._id_cache.get_album_id(album)))
        if artist is not None:
            sets.append(
                self._tracks.get_by_artist(
                    self._id_cache.get_artist_id(artist)))
        if genre is not None:
            sets.append(
                self._tracks.get_by_genre(
                    self._id_cache.get_genre_id(genre)))
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
