# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Various in-memory stores for music collection metadata."""

from __future__ import absolute_import, unicode_literals
import collections
import logging

import avalon.log
import avalon.util
from avalon.elms import id_name_elm_from_model, track_elm_from_model


class IdLookupCache(object):
    """Cache for looking up the primary key of albums, artists,
    and genres based on their name.
    """
    _logger = avalon.log.get_error_log()

    def __init__(self, dao):
        """Set the DAO to use for looking up albums, artist, and
        genres but do not load anything yet.

        :param avalon.models.ReadOnlyDao dao: DAO for reading from
            the database
        """
        self._dao = dao
        self._by_album = None
        self._by_artist = None
        self._by_genre = None

    @staticmethod
    def _get_id(lookup, val):
        """Get the UUID object associated with the given name from the
        given lookup structure, None if no ID is found or the value isn't
        a string.
        """
        try:
            return lookup[val.lower()]
        except AttributeError:
            return None

    def get_album_id(self, val):
        """Get the UUID object associated with an album name, None if no ID
        is found.

        :param str val: Value to lookup an album ID by
        :return: The ID associated with the value or None
        :rtype: uuid.UUID
        """
        return self._get_id(self._by_album, val)

    def get_artist_id(self, val):
        """Get the UUID object associated with an artist name, None if no ID
        is found.

         :param str val: Value to lookup an artist ID by
        :return: The ID associated with the value or None
        :rtype: uuid.UUID
        """
        return self._get_id(self._by_artist, val)

    def get_genre_id(self, val):
        """Get the UUID object associated with a genre name, None if no ID is
        found.

        :param str val: Value to lookup an genre ID by
        :return: The ID associated with the value or None
        :rtype: uuid.UUID
        """
        return self._get_id(self._by_genre, val)

    def reload(self, session=None):
        """Safely populate various structures used for name to ID
        mappings of albums, artists, and genres from the database
        and return this object.

        .. note::

            If an exception occurs during the update the structures
            may be out of date. However, all structures will correctly
            formed and valid.

        :param sqlalchemy.orm.Session session: Optional database
            session that can be used when loading metadata instead
            of loading metadata on a newly created session. This
            should only used when inserting newly scanned metadata
            into a music collection (when we're inside of a transaction
            that has not yet been committed).
        :return: This object
        :rtype: IdLookupCache
        """
        # Pass the session (might be None) to the DAO, let it decide
        # to either use it, or create a new session to use.
        by_album = self._get_name_id_map(self._dao.get_all_albums(session=session))
        by_artist = self._get_name_id_map(self._dao.get_all_artists(session=session))
        by_genre = self._get_name_id_map(self._dao.get_all_genres(session=session))

        self._by_album = by_album
        self._by_artist = by_artist
        self._by_genre = by_genre

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                'IDs by album using %s mb', avalon.util.get_size_in_mb(self._by_album))
            self._logger.debug(
                'IDs by artist using %s mb', avalon.util.get_size_in_mb(self._by_artist))
            self._logger.debug(
                'IDs by genre using %s mb', avalon.util.get_size_in_mb(self._by_genre))

        return self

    @staticmethod
    def _get_name_id_map(all_models):
        """Get the name to ID mappings for a particular type of entity,
        normalizing the case of the name value using a default dictionary
        configured to return None for missing entries.
        """
        mapping = collections.defaultdict(lambda: None)
        for model in all_models:
            elm = id_name_elm_from_model(model)
            mapping[elm.name.lower()] = elm.id
        return mapping


def get_frozen_mapping(table):
    """Return a copy of a default dictionary (assumed to have sets
    for values) with frozen sets for values.
    """
    out = collections.defaultdict(frozenset)

    for key in table:
        out[key] = frozenset(table[key])
    return out


class TrackStore(object):
    """ In-memory store for TrackElm objects and methods to fetch
    them by their attributes.
    """
    _logger = avalon.log.get_error_log()

    def __init__(self, dao):
        """Set the DAO to use for populating various lookup structures
        but to not load anything yet.

        :param avalon.models.ReadOnlyDao dao: DAO for reading from
            the database
        """
        self._dao = dao
        self._by_album = {}
        self._by_artist = {}
        self._by_genre = {}
        self._by_id = {}
        self._all = frozenset()

    def __len__(self):
        return len(self._all)

    def reload(self):
        """Safely populate the various structures for looking
        up track elements by their attributes and return this
        object.

        Note that if an exception occurs during the update the
        structures may be out of date. However, all structures
        will correctly formed and valid.
        """
        all_models = self._dao.get_all_tracks()
        by_album = collections.defaultdict(set)
        by_artist = collections.defaultdict(set)
        by_genre = collections.defaultdict(set)
        by_id = collections.defaultdict(set)
        all_tracks = set()

        for track in all_models:
            elm = track_elm_from_model(track)
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

        # Check if DEBUG is enabled since getting memory usage is slow
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                '%s by album using %s mb', self.__class__.__name__,
                avalon.util.get_size_in_mb(self._by_album))
            self._logger.debug(
                '%s by artist using %s mb', self.__class__.__name__,
                avalon.util.get_size_in_mb(self._by_artist))
            self._logger.debug(
                '%s by genre using %s mb', self.__class__.__name__,
                avalon.util.get_size_in_mb(self._by_genre))
            self._logger.debug(
                '%s by ID using %s mb', self.__class__.__name__,
                avalon.util.get_size_in_mb(self._by_id))
            self._logger.debug(
                '%s all elements using %s mb', self.__class__.__name__,
                avalon.util.get_size_in_mb(self._all))

        return self

    def get_by_album(self, album_id):
        """Get a :class:`frozenset` of tracks by an album UUID, empty frozenset
        if there are no tracks with that album UUID.

        :param uuid.UUID album_id: Album ID to look up tracks by
        :return: All tracks on the given album
        :rtype: frozenset
        """
        return self._by_album[album_id]

    def get_by_artist(self, artist_id):
        """Get a :class:`frozenset` of tracks by an artist UUID, empty frozenset
        if there are no tracks with that artist UUID.

        :param uuid.UUID artist_id: Artist ID to look up tracks by
        :return: All tracks by the given artist
        :rtype: frozenset
        """
        return self._by_artist[artist_id]

    def get_by_genre(self, genre_id):
        """Get a :class:`frozenset` of tracks by a genre UUID, empty frozenset
        if there are no tracks with that genre UUID.

        :param uuid.UUID genre_id: Genre ID to look up tracks by
        :return: All tracks in the given genre
        :rtype: frozenset
        """
        return self._by_genre[genre_id]

    def get_by_id(self, track_id):
        """Get a :class:`frozenset` of tracks by a track UUID, empty frozenset
        if there are no tracks with that UUID. This should only ever return a
        single track but we return a set anyway to consistency with the other
        methods in this class.

        :param uuid.UUID track_id: Track ID to fetch tracks by
        :return: All tracks with the given ID
        :rtype: frozenset
        """
        return self._by_id[track_id]

    def get_all(self):
        """Get a :class:`frozenset` of all tracks.

        :return: All tracks
        :rtype: frozenset
        """
        return self._all


class _IdNameStore(object):
    """Base store for any ID and name element."""
    _logger = avalon.log.get_error_log()

    def __init__(self, dao_method):
        """Set the method of the DAO to use for populating the
        ID-name store but do not load anything yet.
        """
        self._dao_method = dao_method
        self._by_id = {}
        self._all = frozenset()

    def __len__(self):
        return len(self._all)

    def reload(self):
        """Populate all of the ID-name elements and return this
        object.
        """
        all_models = self._dao_method()
        by_id = collections.defaultdict(set)
        all_elms = set()

        for model in all_models:
            elm = id_name_elm_from_model(model)
            by_id[elm.id].add(elm)
            all_elms.add(elm)

        self._by_id = get_frozen_mapping(by_id)
        self._all = frozenset(all_elms)

        # Check if DEBUG is enabled since getting memory usage is slow
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                '%s by ID using %s mb', self.__class__.__name__,
                avalon.util.get_size_in_mb(self._by_id))
            self._logger.debug(
                '%s all elements using %s mb', self.__class__.__name__,
                avalon.util.get_size_in_mb(self._all))

        return self

    def get_by_id(self, elm_id):
        """Get a :class:`frozenset` of elements by their UUID, empty frozenset
         if there are no elements with that UUID.

        :return Elements by their ID
        :rtype: frozenset
        """
        return self._by_id[elm_id]

    def get_all(self):
        """Get a :class:`frozenset` of all elements in the store.

        :return: All elements in the store
        :rtype: frozenset
        """
        return self._all


class AlbumStore(_IdNameStore):
    """In-memory store for Album models using IdNameElm."""

    def __init__(self, dao):
        super(AlbumStore, self).__init__(dao.get_all_albums)


class ArtistStore(_IdNameStore):
    """In-memory store for Artist models using IdNameElm."""

    def __init__(self, dao):
        super(ArtistStore, self).__init__(dao.get_all_artists)


class GenreStore(_IdNameStore):
    """In-memory store for Genre models using IdNameElm."""

    def __init__(self, dao):
        super(GenreStore, self).__init__(dao.get_all_genres)
