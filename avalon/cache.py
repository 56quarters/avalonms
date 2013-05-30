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


"""Various in-memory stores for metadata."""

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
        session = self._session_handler.get_session()
        try:
            return session.query(cls).all()
        finally:
            self._session_handler.close(session)


class IdLookupCache(object):
    """Cache for looking up the primary key of albums, artists,
    and genres based on their name.
    """

    def __init__(self, dao):
        """Set the DAO and use it to initialize ID caches."""
        self._dao = dao
        self._by_album = {}
        self._by_artist = {}
        self._by_genre = {}
        self.reload()

    def _get_id(self, lookup, val):
        """Get the UUID object associated with the given name from the
        given lookup structure, None if no ID is found or the value isn't
        a string.
        """
        try:
            return lookup[val.lower()]
        except AttributeError:
            return None
        except KeyError:
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
        mappings of albums, artists, and genres from the database.

        Note that if an exception occurs during the update the
        structures may be of date. However, all structures will
        correctly formed and valid.
        """
        self._by_album = self._get_name_id_map(self._dao.get_all_albums())
        self._by_artist = self._get_name_id_map(self._dao.get_all_artists())
        self._by_genre = self._get_name_id_map(self._dao.get_all_genres())

    def _get_name_id_map(self, all_models):
        """Get the name to ID mappings for a particular type of entity,
        normalizing the case of the name value.
        """
        mapping = {}
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


class TrackStore(object):
    """ In-memory store for TrackElm objects and methods to fetch
    them by their attributes.
    """

    def __init__(self, dao):
        """Initialize lookup structures and populate them with the DAO."""
        self._dao = dao
        self._by_album = None
        self._by_artist = None
        self._by_genre = None
        self._by_id = None
        self._all = None

        self.reload()

    def reload(self):
        """Safely populate the various structures for looking
        up track elements by their attributes.

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

    def by_album(self, album_id):
        """Get tracks by an album UUID, empty set if there are no tracks
        with that album UUID.
        """
        return self._by_album[album_id]

    def by_artist(self, artist_id):
        """Get tracks by an artist UUID, empty set if there are no tracks
        with that artist UUID.
        """
        return self._by_artist[artist_id]

    def by_genre(self, genre_id):
        """Get tracks by a genre UUID, empty set if there are no tracks
        with that genre UUID.
        """
        return self._by_genre[genre_id]

    def by_id(self, track_id):
        """Get tracks by a track UUID, empty set if there are no tracks
        with that UUID.
        """
        return self._by_id[track_id]

    def all(self):
        """Get all tracks."""
        return self._all


class _IdNameStore(object):
    """Base store for any ID and name element."""

    def __init__(self, dao_method):
        """Set the method of the DAO to use for populating the
        ID-name store.
        """
        self._dao_method = dao_method
        self._by_id = None
        self._all = None

        self.reload()

    def reload(self):
        """Populate all of the ID-name elements."""
        all_models = self._dao_method()
        by_id = collections.defaultdict(set)
        all_elms = set()

        for model in all_models:
            elm = IdNameElm.from_model(model)
            by_id[elm.id].add(elm)
            all_elms.add(elm)

        self._by_id = get_frozen_mapping(by_id)
        self._all = frozenset(all_elms)

    def by_id(self, elm_id):
        """Get elements by their UUID, empty set if there are no elements
        with that UUID.
        """
        return self._by_id[elm_id]

    def all(self):
        """Get all elements in the store."""
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

