# -*- coding: utf-8 -*-
#


""" Classes that encompass business logic spaning multiple
    functional areas.
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

    def get_id(self, field, val):
        """ Get the ID associated with the give field and
            name, 0 if no ID is found.
        """
        try:
            return self._cache[field][val]
        except KeyError:
            return 0

    def load(self):
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
