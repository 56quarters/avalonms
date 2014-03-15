# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


"""Functionality for loading various audio tag metadata into the database."""

import sqlalchemy.exc

import avalon.exc

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
        except sqlalchemy.exc.OperationalError, e:
            raise avalon.exc.OperationalError(str(e))
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
        queued = []
        for tag in self._tags:
            queued.append(self._get_new_obj(cls, id_gen, tag))

        session = self._session_handler.get_session()
        try:
            session.add_all(queued)
            session.commit()
        except sqlalchemy.exc.OperationalError, e:
            raise avalon.exc.OperationalError(str(e))
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

    def clean_type(self, cls):
        """Delete all entities of the given class."""
        session = self._session_handler.get_session()
        try:
            session.query(cls).delete()
            session.commit()
        except sqlalchemy.exc.OperationalError, e:
            raise avalon.exc.OperationalError(str(e))
        finally:
            self._session_handler.close(session)

