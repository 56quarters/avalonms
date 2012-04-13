# -*- coding: utf-8 -*-
#


"""
"""


from avalon.models import (
    Album,
    Artist,
    Genre,
    Track)


__all__ = [
    'IdService',
    'InsertService'
    ]



class IdService(object):

    def __init__(self, session_handler, case_insensitive=False):
        self._session_handler = session_handler
        self._case_insensitive = case_insensitive
        self._cache = {
            'album': {},
            'artist': {},
            'genre': {}
            }

    def get_id(self, field, val):
        """
        """
        try:
            return self._cache[field][self._get_val(val)]
        except KeyError:
            return 0

    def _get_val(self, val):
        """
        """
        if self._case_insensitive:
            return val.lower()
        return val

    def load(self):
        """
        """
        session = self._session_handler.get_session()

        try:
            self._load_mapping(session, 'album', Album)
            self._load_mapping(session, 'artist', Artist)
            self._load_mapping(session, 'genre', Genre)
        finally:
            session.close()

    def _load_mapping(self, session, field, cls):
        """
        """
        things = session.query(cls).all()
        for thing in things:
            self._cache[field][self._get_val(thing.name)] = thing.id
            

class InsertService(object):

    """
    """

    def __init__(self, scanned, session_handler):
        """
        """
        self._scanned = scanned
        self._session_handler = session_handler

    def _load_relations(self):
        """
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
        """
        """
        for val in values:
            obj = cls()
            obj.name = val
            queue.append(obj)

    def insert_tracks(self):
        """
        """
        self._load_relations()
        cache = IdService(self._session_handler)
        cache.load()

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
