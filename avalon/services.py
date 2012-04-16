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
Classes that encompass business logic spaning multiple functional areas.
"""


import collections

from avalon.models import (
    Album,
    Artist,
    Genre,
    Track)


__all__ = [
    'IdService',
    'InsertService'
    ]



class InsertService(object):

    """ Methods for inserting multiple tracks and all associated
        relations.
    """

    def __init__(self, scanned, session_handler):
        """ Set the list of scan result tags and session handler.
        """
        self._scanned = scanned
        self._session_handler = session_handler

    def _load_relations(self):
        """ Insert relations for each track into the database.
        """
        insert = []
        values = {'album': set(), 'artist': set(), 'genre': set()}
        session = self._session_handler.get_session()

        try:
            for tag in self._scanned:
                # Insert all the values into sets to eliminate
                # duplicates before saving them to the DB.
                for field in ('album', 'artist', 'genre'):
                    values[field].add(getattr(tag, field))

            # Build a list of brand new objects to insert
            self._queue_inserts(insert, values['album'], Album)
            self._queue_inserts(insert, values['artist'], Artist)
            self._queue_inserts(insert, values['genre'], Genre)

            session.add_all(insert)
            session.commit()
        finally:
            session.close()

    def _queue_inserts(self, queue, values, cls):
        """ Generate new objects for insertion for each of the
            given values.
        """
        for val in values:
            obj = cls()
            obj.name = val
            queue.append(obj)

    def insert_tracks(self):
        """ Insert the tracks and all related data.
        """
        self._load_relations()
        cache = IdService(self._session_handler)

        insert = []
        session = self._session_handler.get_session()

        try:
            for tag in self._scanned:
                track = Track()
                track.name = tag.title
                track.track = tag.track
                track.year = tag.year

                track.album_id = cache.get_id('album', tag.album)
                track.artist_id = cache.get_id('artist', tag.artist)
                track.genre_id = cache.get_id('genre', tag.genre)

                insert.append(track)
            session.add_all(insert)
            session.commit()
        finally:
            session.close()


class IdService(object):

    """ Cache for looking up the primary key of albums,
        artists, and genres based on their name.
    """

    def __init__(self, session_handler):
        """ Set the session handler and initialize ID caches.
        """
        self._session_handler = session_handler
        self._cache = {
            'album': {},
            'artist': {},
            'genre': {}
            }

        self.reload()

    def get_id(self, field, val):
        """ Get the ID associated with the give field and
            name, 0 if no ID is found.
        """
        try:
            return self._cache[field][val]
        except KeyError:
            return 0

    def reload(self):
        """ Load all name to ID mappings from the database.
        """
        session = self._session_handler.get_session()

        try:
            self._load_mapping(session, 'album', Album)
            self._load_mapping(session, 'artist', Artist)
            self._load_mapping(session, 'genre', Genre)
        finally:
            session.close()

    def _load_mapping(self, session, field, cls):
        """ Set each of the mappings for a particular type of
            entity.
        """
        things = session.query(cls).all()
        for thing in things:
            self._cache[field][thing.name] = thing.id
            

class TrackStore(object):

    """
    """

    def __init__(self, session_handler):
        """
        """
        self._session_handler = session_handler
        self._id_cache = IdService(self._session_handler)

        self._by_album = collections.defaultdict(set)
        self._by_artist = collections.defaultdict(set)
        self._by_genre = collections.defaultdict(set)
        self._all = set()

        self.reload()

    def reload(self):
        """
        """
        session = self._session_handler.get_session()
        
        try:
            res = session.query(Track).all()
        finally:
            self._session_handler.close(session)

        for track in res:
            data = track.to_elm()
            self._by_album[track.album_id].add(data)
            self._by_artist[track.artist_id].add(data)
            self._by_genre[track.genre_id].add(data)
            self._all.add(data)

    def by_album(self, album_id):
        """
        """
        return self._by_album[album_id]

    def by_artist(self, artist_id):
        """
        """
        return self._by_artist[artist_id]

    def by_genre(self, genre_id):
        """
        """
        return self._by_genre[genre_id]

    def all(self):
        """
        """
        return self._all

class _IdNameStore(object):

    """
    """

    def __init__(self, session_handler, cls):
        """
        """
        self._session_handler = session_handler
        self._cls = cls
        self._all = None

        self.reload()

    def reload(self):
        """
        """
        session = self._session_handler.get_session()
        
        try:
            res = session.query(self._cls).all()
        finally:
            self._session_handler.close(session)
        self._all = [thing.to_elm() for thing in res]

    def all(self):
        """
        """
        return self._all


class AlbumStore(_IdNameStore):

    """
    """

    def __init__(self, session_handler):
        """
        """
        super(AlbumStore, self).__init__(session_handler, Album)


class ArtistStore(_IdNameStore):

    """
    """

    def __init__(self, session_handler):
        """
        """
        super(ArtistStore, self).__init__(session_handler, Artist)


class GenreStore(_IdNameStore):

    """
    """

    def __init__(self, session_handler):
        """
        """
        super(GenreStore, self).__init__(session_handler, Genre)
