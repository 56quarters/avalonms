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

