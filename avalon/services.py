# -*- coding: utf-8 -*-
#


"""
"""


from avalon.models import (
    Album,
    Artist,
    Genre,
    Track)


__all__ = []


class InsertService(object):

    """
    """

    def __init__(self, scanned, session):
        """
        """
        self._scanned = scanned
        self._session = session
        self._cache = {
            'album': {},
            'artist': {},
            'genre': {}
            }

    def _get_id(self, field, val):
        """
        """
        return self._cache[field][val].id

    def _load_relations(self):
        """
        """
        insert = []
        
        for tag in self._scanned:
            album = self._populate_relation(tag, 'album', Album)
            artist = self._populate_relation(tag, 'artist', Artist)
            genre = self._populate_relation(tag, 'genre', Genre)

            if album is not None:
                insert.append(album)
            if artist is not None:
                insert.append(artist)
            if genre is not None:
                insert.append(genre)

        self._session.add_all(insert)
        self._session.commit()


    def _populate_relation(self, tag, field, model_cls):
        """
        """
        cache = self._cache[field]
        val = getattr(tag, field)

        if val in cache:
            return None

        obj = model_cls()
        obj.name = val
        cache[val] = obj
        return obj

    def insert_tracks(self):
        """
        """
        self._load_relations()
        insert = []

        for tag in self._scanned:
            track = Track()
            track.name = tag.title
            track.track = tag.track
            track.year = tag.year

            track.album_id = self._get_id('album', tag.album)
            track.artist_id = self._get_id('artist', tag.artist)
            track.genre_id = self._get_id('genre', tag.genre)

            insert.append(track)
        self._session.add_all(insert)
        self._session.commit()
