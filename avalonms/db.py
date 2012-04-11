# -*- coding: utf-8 -*-


class InsertCache(object):

    def __init__(self, scanned, session):
        """
        """
        self._scanned = scanned
        self._session = session
        self._artists = {}
        self._albums = {}
        self._genres = {}
        self._queued = []

    def _load(self):
        for track in self._scanned:
            self._populate(track)

        self._session.add_all(self._queued)
        self._session.commit()

    def _populate(self, track):
        artist = track.artist
        album = track.album
        genre = track.genre

        if artist not in self._artists:
            obj = avalonms.models.Artist()
            obj.name = artist
            self._artists[artist] = obj
            self._queued.append(obj)

        if album not in self._albums:
            obj = avalonms.models.Album()
            obj.name = album
            self._albums[album] = obj
            self._queued.append(obj)

        if genre not in self._genres:
            obj = avalonms.models.Genre()
            obj.name = genre
            self._genres[genre] = obj
            self._queued.append(obj)

            
