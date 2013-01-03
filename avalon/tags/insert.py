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


"""Functionality for loading various audio tag metadata into the database."""


__all__ = [
    'TrackFieldLoader',
    'TrackLoader',
    'Cleaner'
    ]


class TrackFieldLoader(object):

    """Create and insert entries for the associated data for each
    tag (albums, artists, genres).
    """

    def __init__(self, session_handler, tags):
        """Set the session handler and tags."""
        self._session_handler = session_handler
        self._tags = tags

    def insert(self, cls, id_gen, field):
        """Insert entries for the associated data for each tag
        using the given model class, ID generator, and field of
        the metadata tag.
        """
        queued = {}
        for tag in self._tags:
            obj = self._get_new_obj(cls, id_gen, field, tag)
            queued[obj.id] = obj

        session = self._session_handler.get_session()
        try:
            session.add_all(queued.values())
            session.commit()
        finally:
            self._session_handler.close(session)

    def _get_new_obj(self, cls, id_gen, field, tag):
        """Generate a new model object for associated data for
        an audio tag.
        """
        val = getattr(tag, field, None)
        if val is None:
            # Raise an AttributeError (which would have happened
            # anyway) with some additional information to help with
            # find invalid audio tags.
            raise AttributeError(
                "Invalid tag field [%s] for [%s]" % (field, tag.path))
        obj = cls()
        obj.id = id_gen(val)
        obj.name = val
        return obj


class TrackLoader(object):

    """Create and insert entries for each tag and associated IDs."""

    def __init__(self, session_handler, tags, id_cache):
        """Set the session handler, tags, and ID lookup cache."""
        self._session_handler = session_handler
        self._tags = tags
        self._id_cache = id_cache

    def insert(self, cls, id_gen):
        """Insert entries for each audio metadata tag using the
        given model class and ID generator along with associated
        IDs for albums, artists, and genres.
        """
        queue = []
        for tag in self._tags:
            queue.append(self._get_new_obj(cls, id_gen, tag)) 

        session = self._session_handler.get_session()
        try:
            session.add_all(queue)
            session.commit()
        finally:
            self._session_handler.close(session)

    def _get_new_obj(self, cls, id_gen, tag):
        """Generate a new model object for an audio tag and set
        the associated IDs for albums, artists, and genres.
        """
        obj = cls()
        obj.id = id_gen(tag.path)
        obj.name = tag.title
        obj.length = tag.length
        obj.track = tag.track
        obj.year = tag.year

        obj.album_id = self._id_cache.get_album_id(tag.album)
        obj.artist_id = self._id_cache.get_artist_id(tag.artist)
        obj.genre_id = self._id_cache.get_genre_id(tag.genre)

        return obj


class Cleaner(object):

    """Cleaner for removing already inserted entities."""

    def __init__(self, session_handler):
        """Set the session handler."""
        self._session_handler = session_handler

    def clean_all(self, cls):
        """Delete all entities of the given class."""
        session = self._session_handler.get_session()
        try:
            session.query(cls).delete()
            session.commit()
        finally:
            self._session_handler.close(session)

