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


