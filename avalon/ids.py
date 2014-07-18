# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Methods for generating stable IDs for albums, artists, genres, and tracks."""

from __future__ import unicode_literals
import uuid

from avalon.compat import to_uuid_input


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
    """Normalize a text type by converting it to lower case and
    then converting to the correct type to be used as UUID input
    (varies depending on the version of Python running).
    """
    return to_uuid_input(value.lower())


def get_album_id(name):
    """Generate a UUID based on the album name (case insensitive).

    :param unicode name: Name of the album
    :return: UUID based on the name of the album
    :rtype: uuid.UUID
    """
    return uuid.uuid5(NS_ALBUMS, _normalize_no_case(name))


def get_artist_id(name):
    """Generate a UUID based on the artist name (case insensitive).

    :param unicode name: Name of the artist
    :return: UUID based on the name of the artist
    :rtype: uuid.UUID
    """
    return uuid.uuid5(NS_ARTISTS, _normalize_no_case(name))


def get_genre_id(name):
    """Generate a UUID based on the genre name (case insensitive).

    :param unicode name: Name of the genre
    :return: UUID based on the name of the genre
    :rtype: uuid.UUID
    """
    return uuid.uuid5(NS_GENRES, _normalize_no_case(name))


def get_track_id(path):
    """Generate a UUID based on the path of a track (case sensitive).

    :param unicode path: Absolute path to a track
    :return: UUID based on the path of the track
    :rtype: uuid.UUID
    """
    return uuid.uuid5(NS_TRACKS, to_uuid_input(path))
