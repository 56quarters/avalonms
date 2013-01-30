# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2013 TSH Labs <projects@tshlabs.org>
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


"""Methods for generating stable IDs for albums, artists, genres, and tracks."""


import uuid

import avalon


__all__ = [
    'NS_ALBUMS',
    'NS_ARTISTS',
    'NS_GENRES',
    'NS_TRACKS',
    'get_album_id',
    'get_artist_id',
    'get_genre_id',
    'get_track_id'
    ]


NS_ALBUMS = uuid.UUID('7655e605-6eaa-40d8-a25f-5c6c92a4d31a')
NS_ARTISTS = uuid.UUID('fe4df0f6-2c55-4ba6-acf3-134eae3e710e')
NS_GENRES = uuid.UUID('dd8dbd9c-8ed7-4719-80c5-71d978665dd0')
NS_TRACKS = uuid.UUID('4151ace3-6a98-41cd-a3de-8c242654cb67')


def _normalize_no_case(value):
    """Return a normalized case insensitive version of the input."""
    return _normalize(value.lower())


def _normalize(value):
    """Return a normalized version of the input."""
    return value.encode(avalon.DEFAULT_ENCODING)


def get_album_id(name):
    """Generate a UUID based on the album name (case insensitive)."""
    return uuid.uuid5(NS_ALBUMS, _normalize_no_case(name))


def get_artist_id(name):
    """Generate a UUID based on the artist name (case insensitive)."""
    return uuid.uuid5(NS_ARTISTS, _normalize_no_case(name))


def get_genre_id(name):
    """Generate a UUID based on the genre name (case insensitive)."""
    return uuid.uuid5(NS_GENRES, _normalize_no_case(name))


def get_track_id(path):
    """Generate a UUID based on the path of a track (case sensitive)."""
    return uuid.uuid5(NS_TRACKS, _normalize(path))

