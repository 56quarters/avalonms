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


"""
Classes that encompass business logic spanning multiple functional
areas.
"""

import collections

import avalon.ids
from avalon.models import Album, Artist, Genre, Track
from avalon.elms import IdNameElm, TrackElm


__all__ = [
    'AlbumStore',
    'ArtistStore',
    'GenreStore',
    'IdLookupCache',
    'InsertService',
    'TrackStore'
    ]


class InsertService(object):

    """Methods for inserting multiple tracks and all associated
    relations.
    """

    def __init__(self, session_handler, id_cache):
        """Set the list of scan result tags and session handler."""
        self._session_handler = session_handler
        self._id_cache = id_cache

    def _load_relations(self, scanned):
        """Insert relations for each track into the database."""
        inserts = []
        values = {'album': list(), 'artist': list(), 'genre': list()}
        session = self._session_handler.get_session()

        try:
            for tag in scanned:
                for field in ('album', 'artist', 'genre'):
                    values[field].append(getattr(tag, field))

            # Build a list of brand new objects to insert
            inserts.extend(
                self._get_queued_models(
                    values['album'], 
                    Album, 
                    avalon.ids.get_album_id))
            inserts.extend(
                self._get_queued_models(
                    values['artist'], 
                    Artist, 
                    avalon.ids.get_artist_id))
            inserts.extend(
                self._get_queued_models(
                    values['genre'], 
                    Genre, 
                    avalon.ids.get_genre_id))

            session.add_all(inserts)
            session.commit()
        finally:
            self._session_handler.close(session)

    def _get_queued_models(self, values, cls, id_gen):
        """Generate new objects for insertion for each of the given values."""
        out = {}
        for val in values:
            obj = cls()
            obj.id = id_gen(val)
            obj.name = val

            # Add each object to a map indexed by ID so that we
            # filter out dupes using the same mechanism as the ID 
            # generation.
            out[obj.id] = obj
        return out.values()

    def _clean(self):
        """Delete all the things."""
        session = self._session_handler.get_session()

        try:
            session.query(Album).delete()
            session.query(Artist).delete()
            session.query(Genre).delete()
            session.query(Track).delete()
            session.commit()
        finally:
            self._session_handler.close(session)

    def insert(self, scanned):
        """Insert the tracks and all related data."""
        self._clean()
        self._load_relations(scanned)
        self._id_cache.reload()

        insert = []
        session = self._session_handler.get_session()

        try:
            for tag in scanned:
                track = Track()
                track.id = avalon.ids.get_track_id(tag.path)
                track.name = tag.title
                track.track = tag.track
                track.year = tag.year

                track.album_id = self._id_cache.get_album_id(tag.album)
                track.artist_id = self._id_cache.get_artist_id(tag.artist)
                track.genre_id = self._id_cache.get_genre_id(tag.genre)

                insert.append(track)
            session.add_all(insert)
            session.commit()
        finally:
            self._session_handler.close(session)


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
        """Get the ID associated with the give field and name, blank string if
        no ID is found.
        """
        try:
            return self._cache[field][val.lower()]
        except AttributeError:
            return ''
        except KeyError:
            return ''

    def get_album_id(self, val):
        """Get the ID associated with an album name, blank string if no ID is found."""
        return self._get_id('album', val)

    def get_artist_id(self, val):
        """Get the ID associated with an artist name, blank string if no ID is found."""
        return self._get_id('artist', val)

    def get_genre_id(self, val):
        """Get the ID associated with an genre name, blank string if no ID is found."""
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


class TrackStore(object):

    """ In memory store for TrackElm objects and methods to fetch
    them by their attributes.
    """

    def __init__(self, session_handler):
        """Initialize lookup structures and populate them."""
        self._session_handler = session_handler
        self._by_album = None
        self._by_artist = None
        self._by_genre = None
        self._all = None

        self.reload()

    def _freeze(self, table):
        """Return a copy of a dictionary with mutable setS for values
        replaced with frozensetS for values.
        """
        out = collections.defaultdict(frozenset)

        for key in table:
            out[key] = frozenset(table[key])
        return out

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
        all_tracks = set()

        for track in res:
            elm = TrackElm.from_model(track)
            by_album[elm.album_id].add(elm)
            by_artist[elm.artist_id].add(elm)
            by_genre[elm.genre_id].add(elm)
            all_tracks.add(elm)

        self._by_album = self._freeze(by_album)
        self._by_artist = self._freeze(by_artist)
        self._by_genre = self._freeze(by_genre)
        self._all = frozenset(all_tracks)

    def by_album(self, album_id):
        """Get tracks by an album ID."""
        return self._by_album[album_id]

    def by_artist(self, artist_id):
        """Get tracks by an artist ID."""
        return self._by_artist[artist_id]

    def by_genre(self, genre_id):
        """Get tracks by a genre ID."""
        return self._by_genre[genre_id]

    def all(self):
        """Get all tracks."""
        return self._all


class _IdNameStore(object):

    """Base store for any ID and name element."""

    def __init__(self, session_handler, cls):
        """Load all elements of the given type."""
        self._session_handler = session_handler
        self._cls = cls
        self._all = None

        self.reload()

    def reload(self):
        """Atomically populate all elements of the given type."""
        session = self._session_handler.get_session()
        
        try:
            res = session.query(self._cls).all()
        finally:
            self._session_handler.close(session)
        self._all = frozenset(IdNameElm.from_model(thing) for thing in res)

    def all(self):
        """Get all elements."""
        return self._all


class AlbumStore(_IdNameStore):

    """In memory store for Album models using IdNameElm."""

    def __init__(self, session_handler):
        super(AlbumStore, self).__init__(session_handler, Album)


class ArtistStore(_IdNameStore):

    """In memory store for Artist models using IdNameElm."""

    def __init__(self, session_handler):
        super(ArtistStore, self).__init__(session_handler, Artist)


class GenreStore(_IdNameStore):

    """In memory store for Genre models using IdNameElm."""

    def __init__(self, session_handler):
        super(GenreStore, self).__init__(session_handler, Genre)

