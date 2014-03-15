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


"""Various in-memory stores for music collection metadata."""

import collections

from avalon.elms import IdNameElm, TrackElm
from avalon.models import Album, Artist, Genre, Track


__all__ = [
    'AlbumStore',
    'ArtistStore',
    'GenreStore',
    'IdLookupCache',
    'ReadOnlyDao',
    'TrackStore',
    'get_frozen_mapping'
]


class ReadOnlyDao(object):
    """Read-only DAO for loading each type of model object by
    making use of the :class:`SessionHandler` and each associated
    model class.

    This class doesn't add a lot of functionality on top of the
    :class:`SessionHandler`, it's just a facade to allow consumers
    to be tested more easily."""

    def __init__(self, session_handler):
        """Set the session handler to use for fetching models."""
        self._session_handler = session_handler

    def get_all_albums(self):
        """Get a list of all Album models in the database"""
        return self._get_all_cls(Album)

    def get_all_artists(self):
        """Get a list of all Artist models in the database"""
        return self._get_all_cls(Artist)

    def get_all_genres(self):
        """Get a list of all Genre models in the database"""
        return self._get_all_cls(Genre)

    def get_all_tracks(self):
        """Get a list of all Track models in the database"""
        return self._get_all_cls(Track)

    def _get_all_cls(self, cls):
        """Get a list of all models by the given class."""
        with self._session_handler.get_scoped_session() as session:
            return session.query(cls).all()


class IdLookupCache(object):
    """Cache for looking up the primary key of albums, artists,
    and genres based on their name.
    """

    def __init__(self, dao):
        """Set the DAO to use for looking up albums, artist, and
        genres but do not load anything yet.
        """
        self._dao = dao
        self._by_album = None
        self._by_artist = None
        self._by_genre = None

    def _get_id(self, lookup, val):
        """Get the UUID object associated with the given name from the
        given lookup structure, None if no ID is found or the value isn't
        a string.
        """
        try:
            return lookup[val.lower()]
        except AttributeError:
            return None

    def get_album_id(self, val):
        """Get the UUID object associated with an album name, None if no ID
        is found.
        """
        return self._get_id(self._by_album, val)

    def get_artist_id(self, val):
        """Get the UUID object associated with an artist name, None if no ID
        is found.
        """
        return self._get_id(self._by_artist, val)

    def get_genre_id(self, val):
        """Get the UUID object associated with a genre name, None if no ID is
        found.
        """
        return self._get_id(self._by_genre, val)

    def reload(self):
        """Safely populate various structures used for name to ID
        mappings of albums, artists, and genres from the database
        and return this object.

        Note that if an exception occurs during the update the
        structures may be of date. However, all structures will
        correctly formed and valid.
        """
        by_album = self._get_name_id_map(self._dao.get_all_albums())
        by_artist = self._get_name_id_map(self._dao.get_all_artists())
        by_genre = self._get_name_id_map(self._dao.get_all_genres())

        self._by_album = by_album
        self._by_artist = by_artist
        self._by_genre = by_genre
        return self

    def _get_name_id_map(self, all_models):
        """Get the name to ID mappings for a particular type of entity,
        normalizing the case of the name value using a default dictionary
        configured to return None for missing entries.
        """
        mapping = collections.defaultdict(_missing_entry)
        for model in all_models:
            elm = IdNameElm.from_model(model)
            mapping[elm.name.lower()] = elm.id
        return mapping


def get_frozen_mapping(table):
    """Return a copy of a default dictionary (assumed to have sets
    for values) with frozen sets for values.
    """
    out = collections.defaultdict(frozenset)

    for key in table:
        out[key] = frozenset(table[key])
    return out


def _missing_entry():
    """Factory to return None for missing entries in a default dictionary"""
    return None


class TrackStore(object):
    """ In-memory store for TrackElm objects and methods to fetch
    them by their attributes.
    """

    def __init__(self, dao):
        """Set the DAO to use for populating various lookup structures
        but to not load anything yet.
        """
        self._dao = dao
        self._by_album = None
        self._by_artist = None
        self._by_genre = None
        self._by_id = None
        self._all = None

    def reload(self):
        """Safely populate the various structures for looking
        up track elements by their attributes and return this
        object.

        Note that if an exception occurs during the update the
        structures may be of date. However, all structures will
        correctly formed and valid.
        """
        all_models = self._dao.get_all_tracks()
        by_album = collections.defaultdict(set)
        by_artist = collections.defaultdict(set)
        by_genre = collections.defaultdict(set)
        by_id = collections.defaultdict(set)
        all_tracks = set()

        for track in all_models:
            elm = TrackElm.from_model(track)
            by_album[elm.album_id].add(elm)
            by_artist[elm.artist_id].add(elm)
            by_genre[elm.genre_id].add(elm)
            by_id[elm.id].add(elm)
            all_tracks.add(elm)

        self._by_album = get_frozen_mapping(by_album)
        self._by_artist = get_frozen_mapping(by_artist)
        self._by_genre = get_frozen_mapping(by_genre)
        self._by_id = get_frozen_mapping(by_id)
        self._all = frozenset(all_tracks)
        return self

    def get_by_album(self, album_id):
        """Get a :class:`frozenset` of tracks by an album UUID, empty frozenset
        if there are no tracks with that album UUID.
        """
        return self._by_album[album_id]

    def get_by_artist(self, artist_id):
        """Get a :class:`frozenset` of tracks by an artist UUID, empty frozenset
        if there are no tracks with that artist UUID.
        """
        return self._by_artist[artist_id]

    def get_by_genre(self, genre_id):
        """Get a :class:`frozenset` of tracks by a genre UUID, empty frozenset
        if there are no tracks with that genre UUID.
        """
        return self._by_genre[genre_id]

    def get_by_id(self, track_id):
        """Get a :class:`frozenset` of tracks by a track UUID, empty frozenset
        if there are no tracks with that UUID.
        """
        return self._by_id[track_id]

    def get_all(self):
        """Get a :class:`frozenset` of all tracks."""
        return self._all


class _IdNameStore(object):
    """Base store for any ID and name element."""

    def __init__(self, dao_method):
        """Set the method of the DAO to use for populating the
        ID-name store but do not load anything yet.
        """
        self._dao_method = dao_method
        self._by_id = None
        self._all = None

    def reload(self):
        """Populate all of the ID-name elements and return this
        object.
        """
        all_models = self._dao_method()
        by_id = collections.defaultdict(set)
        all_elms = set()

        for model in all_models:
            elm = IdNameElm.from_model(model)
            by_id[elm.id].add(elm)
            all_elms.add(elm)

        self._by_id = get_frozen_mapping(by_id)
        self._all = frozenset(all_elms)
        return self

    def get_by_id(self, elm_id):
        """Get a :class:`frozenset` of elements by their UUID, empty frozenset
         if there are no elements with that UUID.
        """
        return self._by_id[elm_id]

    def get_all(self):
        """Get a :class:`frozenset` of all elements in the store."""
        return self._all


class AlbumStore(_IdNameStore):
    """In-memory store for Album models using IdNameElm."""

    def __init__(self, dao):
        super(AlbumStore, self).__init__(dao.get_all_albums)


class ArtistStore(_IdNameStore):
    """In-memory store for Artist models using IdNameElm."""

    def __init__(self, dao):
        super(ArtistStore, self).__init__(dao.get_all_artists)


class GenreStore(_IdNameStore):
    """In-memory store for Genre models using IdNameElm."""

    def __init__(self, dao):
        super(GenreStore, self).__init__(dao.get_all_genres)

