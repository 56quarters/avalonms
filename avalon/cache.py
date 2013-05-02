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

from avalon.models import Album, Artist, Genre, Track
from avalon.elms import IdNameElm, TrackElm


__all__ = [
    'AlbumStore',
    'ArtistStore',
    'GenreStore',
    'IdLookupCache',
    'TrackStore',
    'get_frozen_mapping'
]


class IdLookupCache(object):
    """Cache for looking up the primary key of albums, artists,
    and genres based on their name.
    """

    def __init__(self, session_handler):
        """Set the session handler and initialize ID caches."""
        self._session_handler = session_handler
        self._cache = {}
        self.reload()

    def _get_id(self, field, val):
        """Get the UUID object associated with the give field and name, None if
        no ID is found.
        """
        try:
            return self._cache[field][val.lower()]
        except AttributeError:
            return None
        except KeyError:
            return None

    def get_album_id(self, val):
        """Get the UUID object associated with an album name, None if no ID is found."""
        return self._get_id('album', val)

    def get_artist_id(self, val):
        """Get the UUID object associated with an artist name, None if no ID is found."""
        return self._get_id('artist', val)

    def get_genre_id(self, val):
        """Get the UUID object associated with a genre name, None if no ID is found."""
        return self._get_id('genre', val)

    def reload(self):
        """Atomically load all name to ID mappings from the database."""
        session = self._session_handler.get_session()
        cache = {}

        try:
            cache['album'] = self._get_name_id_map(session, Album)
            cache['artist'] = self._get_name_id_map(session, Artist)
            cache['genre'] = self._get_name_id_map(session, Genre)
        finally:
            self._session_handler.close(session)
        self._cache = cache

    def _get_name_id_map(self, session, cls):
        """Get the name to ID mappings for a particular type of entity."""
        field_cache = {}
        for entity in session.query(cls).all():
            elm = IdNameElm.from_model(entity)
            field_cache[elm.name.lower()] = elm.id
        return field_cache


def get_frozen_mapping(table):
    """Return a copy of a dictionary with mutable sets for values
    replaced with frozensets for values.
    """
    out = collections.defaultdict(frozenset)

    for key in table:
        out[key] = frozenset(table[key])
    return out


class TrackStore(object):
    """ In-memory store for TrackElm objects and methods to fetch
    them by their attributes.
    """

    def __init__(self, session_handler):
        """Initialize lookup structures and populate them."""
        self._session_handler = session_handler
        self._by_album = None
        self._by_artist = None
        self._by_genre = None
        self._by_id = None
        self._all = None

        self.reload()

    def reload(self):
        """Atomically populate the various structures for looking
        up track elements by their attributes.
        """
        session = self._session_handler.get_session()

        try:
            res = session.query(Track).all()
        finally:
            self._session_handler.close(session)

        by_album = collections.defaultdict(set)
        by_artist = collections.defaultdict(set)
        by_genre = collections.defaultdict(set)
        by_id = collections.defaultdict(set)
        all_tracks = set()

        for track in res:
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
        """Get tracks by an album ID, empty set if there are no tracks
        with that album ID.
        """
        return self._by_album[album_id]

    def by_artist(self, artist_id):
        """Get tracks by an artist ID, empty set if there are no tracks
        with that artist ID.
        """
        return self._by_artist[artist_id]

    def by_genre(self, genre_id):
        """Get tracks by a genre ID, empty set if there are no tracks
        with that genre ID.
        """
        return self._by_genre[genre_id]

    def by_id(self, track_id):
        """Get tracks by a track ID, empty set if there are no tracks
        with that ID.
        """
        return self._by_id[track_id]

    def all(self):
        """Get all tracks."""
        return self._all


class _IdNameStore(object):
    """Base store for any ID and name element."""

    def __init__(self, session_handler, cls):
        """Load all elements of the given type."""
        self._session_handler = session_handler
        self._cls = cls
        self._by_id = None
        self._all = None

        self.reload()

    def reload(self):
        """Atomically populate all elements of the given type."""
        session = self._session_handler.get_session()

        try:
            res = session.query(self._cls).all()
        finally:
            self._session_handler.close(session)

        by_id = collections.defaultdict(set)
        all_elms = set()

        for thing in res:
            elm = IdNameElm.from_model(thing)
            by_id[elm.id].add(elm)
            all_elms.add(elm)

        self._by_id = get_frozen_mapping(by_id)
        self._all = frozenset(all_elms)

    def by_id(self, elm_id):
        """Get elements by their ID, empty set if there are no elements
        with that ID.
        """
        return self._by_id[elm_id]

    def all(self):
        """Get all elements in the store."""
        return self._all


class AlbumStore(_IdNameStore):
    """In-memory store for Album models using IdNameElm."""

    def __init__(self, session_handler):
        super(AlbumStore, self).__init__(session_handler, Album)


class ArtistStore(_IdNameStore):
    """In-memory store for Artist models using IdNameElm."""

    def __init__(self, session_handler):
        super(ArtistStore, self).__init__(session_handler, Artist)


class GenreStore(_IdNameStore):
    """In-memory store for Genre models using IdNameElm."""

    def __init__(self, session_handler):
        super(GenreStore, self).__init__(session_handler, Genre)

