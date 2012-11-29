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


""" """


import functools


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



class AvalonStatusEndpointsConfig(object):

    def __init__(self):
        pass


class AvalonStatusEndpoints(object):

    def __init__(self, config):
        pass

    def reload(self):
        pass


class AvalonApiEndpointsConfig(object):

    def __init__(self):
        self.track_store = None
        self.album_store = None
        self.artist_store = None
        self.genre_store = None
        self.id_cache = None


class AvalonApiEndpoints(object):

    def __init__(self, config):
        """Initialize each of the stores by loading from the database."""
        self._tracks = config.track_store
        self._albums = config.album_store
        self._artists = config.artist_store
        self._genres = config.genre_store
        self._id_cache = config.id_cache

    def reload(self):
        """Reload in memory stores from the database."""
        self._tracks.reload()
        self._albums.reload()
        self._artists.reload()
        self._genres.reload()
        self._id_cache.reload()

    def get_albums(self):
        """Return a list of all albums."""
        return self._albums.all()

    def get_artists(self):
        """Return a list of all artists."""
        return self._artists.all()

    def get_genres(self):
        """Return a list of all genres."""
        return self._genres.all()

    def get_songs(self, params):
        """Return song results based on the given query string parameters."""
        sets = []

        if None is not params.get('album'):
            sets.append(
                self._tracks.by_album(
                    self._id_cache.get_album_id(params.get('album'))))
        if None is not params.get('artist'):
            sets.append(
                self._tracks.by_artist(
                    self._id_cache.get_artist_id(params.get('artist'))))
        if None is not params.get('genre'):
            sets.append(
                self._tracks.by_genre(
                    self._id_cache.get_genre_id(params.get('genre'))))

        if None is not params.get('album_id'):
            sets.append(self._tracks.by_album(params.get('album_id')))
        if None is not params.get('artist_id'):
            sets.append(self._tracks.by_artist(params.get('artist_id')))
        if None is not params.get('genre_id'):
            sets.append(self._tracks.by_genre(params.get('genre_id')))
            
        if sets:
            # Return the intersection of any non-None sets
            return intersection(sets)
        # There were no parameters to filter songs by any criteria
        return self._tracks.all()


