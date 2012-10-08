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
    """Generate an ID based on the album name (case insensitive)."""
    return uuid.uuid5(NS_ALBUMS, _normalize_no_case(name))


def get_artist_id(name):
    """Generate an ID based on the artist name (case insensitive)."""
    return uuid.uuid5(NS_ARTISTS, _normalize_no_case(name))


def get_genre_id(name):
    """Generate an ID based on the genre name (case insensitive)."""
    return uuid.uuid5(NS_GENRES, _normalize_no_case(name))


def get_track_id(path):
    """Generate an ID based on the path of a track (case sensitive)."""
    return uuid.uuid5(NS_TRACKS, _normalize(path))

