# -*- coding: utf-8 -*-
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


"""
Immutable wrappers for model objects suitable for being rendered
as JSON and an encoder for doing so.
"""


import sys

try:
    import simplejson as json
except ImportError:
    import json


__all__ = [
    'IdNameElm',
    'JSONEncoder',
    'TrackElm'
    ]


class JSONEncoder(json.JSONEncoder):
    
    """ Special JSON encoder to convert the output format from
        services used by the web layer to datatypes that can be
        easily rendered.
    """

    def default(self, o):
        """ Return a dictionary representing IdNameElm or TrackElm objects.
        """
        if not isinstance(o, IdNameElm):
            return super(JSONEncoder, self).default(o)

        if isinstance(o, TrackElm):
            return {
                'id': o.id,
                'name': o.name,
                'track': o.track,
                'year': o.year,
                'album': o.album,
                'album_id': o.album_id,
                'artist': o.artist,
                'artist_id': o.artist_id,
                'genre': o.genre,
                'genre_id': o.genre_id
                }
        return {'id': o.id, 'name': o.name}


class IdNameElm(object):

    """Immutable, hashable representation of a model with ID
    and name attributes (everything besides Tracks).
    """

    def __init__(self, elm_id, elm_name):
        """Set the element attributes."""
        self._id = elm_id
        self._name = elm_name

    @property
    def id(self):
        """Element ID."""
        return self._id

    @property
    def name(self):
        """Element name."""
        return self._name

    def __eq__(self, o):
        """Two instances are equal based on ID and name."""
        if not isinstance(o, self.__class__):
            return False
        return o.id == self.id and o.name == self.name

    def __hash__(self):
        """Hash is computed from ID, name, and class."""
        return hash(self.id) ^ (hash(self.name) * 7) ^ (hash(self.__class__) * 31)

    def __sizeof__(self):
        """Get the size of the object in bytes."""
        size = super(IdNameElm, self).__sizeof__()
        size += sys.getsizeof(self._id)
        size += sys.getsizeof(self._name)
        return size


class TrackElm(IdNameElm):

    """ Immutable, hashable representation of a Track model.
    """

    def __init__(self, t_id, t_name, t_track, t_year,
                 t_album, t_album_id, t_artist, t_artist_id,
                 t_genre, t_genre_id):
        """Set the track attributes."""
        super(TrackElm, self).__init__(t_id, t_name)

        self._track = t_track
        self._year = t_year
        self._album = t_album
        self._album_id = t_album_id
        self._artist = t_artist
        self._artist_id = t_artist_id
        self._genre = t_genre
        self._genre_id = t_genre_id

    def __sizeof__(self):
        """Get the size of the object in bytes."""
        size = super(TrackElm, self).__sizeof__()
        size += sys.getsizeof(self._track)
        size += sys.getsizeof(self._year)
        size += sys.getsizeof(self._album)
        size += sys.getsizeof(self._album_id)
        size += sys.getsizeof(self._artist)
        size += sys.getsizeof(self._artist_id)
        size += sys.getsizeof(self._genre)
        size += sys.getsizeof(self._genre_id)
        return size

    @property
    def track(self):
        """Track track number (seriously)."""
        return self._track

    @property
    def year(self):
        """Track year."""
        return self._year

    @property
    def album(self):
        """Track album name."""
        return self._album

    @property
    def album_id(self):
        """Track album ID."""
        return self._album_id

    @property
    def artist(self):
        """Track artist name."""
        return self._artist

    @property
    def artist_id(self):
        """Track artist ID."""
        return self._artist_id
    
    @property
    def genre(self):
        """Track genre name."""
        return self._genre
    
    @property
    def genre_id(self):
        """Track genre ID."""
        return self._genre_id
