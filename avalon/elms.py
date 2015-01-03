# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Immutable wrappers for model objects suitable for being rendered as JSON.
"""

from __future__ import absolute_import, unicode_literals
import collections


IdNameElm = collections.namedtuple('IdNameElm', ['id', 'name'])


# Note that we're using a separate factory method here (instead of
# a class method) since subclassing a named tuple breaks the __dict__
# attribute somehow in Python 3.
def id_name_elm_from_model(model):
    """Construct a new ID name element from various types of models.

    :param model: Any ID-name type model
    :return: Immutable representation of the given model
    :rtype: IdNameElm
    """
    return IdNameElm(
        id=model.id,
        name=model.name)


TrackElm = collections.namedtuple('TrackElm', [
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
    'genre_id'])


# Note that we're using a separate factory method here (instead of
# a class method) since subclassing a named tuple breaks the __dict__
# attribute somehow in Python 3.
def track_elm_from_model(model):
    """Construct a new track element from a track model.

    :param avalon.models.TrackModel model: Model to construct
        an immutable representation of
    :return: Immutable representation of the given model
    :rtype: TrackElm
    """
    return TrackElm(
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
