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


"""
Immutable wrappers for model objects suitable for being rendered as JSON.
"""

import collections


__all__ = [
    'IdNameElm',
    'TrackElm'
]


class IdNameElm(collections.namedtuple('_IdNameElm', ['id', 'name'])):
    """Immutable, hashable representation of a model with ID
    and name attributes (everything besides Tracks).
    """

    @classmethod
    def from_model(cls, model):
        """Construct a new ID name element from various types of models."""
        return cls(
            id=model.id,
            name=model.name)


class TrackElm(collections.namedtuple('_TrackElm', [
    'id',
    'name',
    'length',
    'track',
    'year',
    'album',
    'album_id',
    'artist',
    'artist_id',
    'genre',
    'genre_id'])):
    """Immutable, hashable representation of a Track model."""

    @classmethod
    def from_model(cls, model):
        """Construct a new track element from a track model."""
        return cls(
            id=model.id,
            name=model.name,
            length=model.length,
            track=model.track,
            year=model.year,
            album=model.album.name,
            album_id=model.album_id,
            artist=model.artist.name,
            artist_id=model.artist_id,
            genre=model.genre.name,
            genre_id=model.genre_id)
