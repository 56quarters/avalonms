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


"""
Immutable wrappers for model objects suitable for being rendered as JSON.
"""

import collections


__all__ = [
    'IdNameElm',
    'TrackElm'
]


class IdNameElm(collections.namedtuple('IdNameElm', ['id', 'name'])):
    """Immutable, hashable representation of a model with ID
    and name attributes (everything besides Tracks).
    """

    @classmethod
    def from_model(cls, model):
        """Construct a new ID name element from various types of models."""
        return cls(
            id=model.id,
            name=model.name)


class TrackElm(collections.namedtuple('TrackElm', [
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
