# -*- coding: utf-8 -*-
#

from __future__ import absolute_import, unicode_literals
import uuid

import pytest
import mock
import avalon.cache
import avalon.models


class TestFunctions(object):
    def test_get_frozen_mapping(self):
        mapping = {'foo': set(['zing', 'zam', 'zowey'])}
        frozen = avalon.cache.get_frozen_mapping(mapping)

        assert 'foo' in frozen
        assert frozen['foo'] == frozenset(['zing', 'zam', 'zowey'])
        assert isinstance(frozen['foo'], frozenset)

        with pytest.raises(AttributeError):
            frozen['foo'].add('blah')


class TestIdLookupCache(object):
    def test_get_album_id_exists(self):
        """Test that we can translate an album name to ID"""
        model1 = avalon.models.Album()
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = 'Dookie'

        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = [model1]
        dao.get_all_artists.return_value = []
        dao.get_all_genres.return_value = []

        cache = avalon.cache.IdLookupCache(dao).reload()

        assert uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a") == \
               cache.get_album_id('Dookie')

    def test_get_album_id_does_not_exist(self):
        """Test that an album that does not exist returns None"""
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = []
        dao.get_all_artists.return_value = []
        dao.get_all_genres.return_value = []

        cache = avalon.cache.IdLookupCache(dao).reload()
        assert None is cache.get_album_id('Dookie')

    def test_get_album_id_case_insensitive(self):
        """Test that we can translate an album name to ID in a case insensitive fasion"""
        model1 = avalon.models.Album()
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = 'Dookie'

        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = [model1]
        dao.get_all_artists.return_value = []
        dao.get_all_genres.return_value = []

        cache = avalon.cache.IdLookupCache(dao).reload()

        assert uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a") == \
               cache.get_album_id('DOOKIE')

    def test_get_artist_id_exists(self):
        """Test that we can translate an artist name to ID"""
        model1 = avalon.models.Album()
        model1.id = uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd")
        model1.name = 'Bad Religion'

        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = []
        dao.get_all_artists.return_value = [model1]
        dao.get_all_genres.return_value = []

        cache = avalon.cache.IdLookupCache(dao).reload()

        assert uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd") == \
               cache.get_artist_id('Bad Religion')

    def test_get_artist_id_does_not_exist(self):
        """Test that an artist that does not exist returns None"""
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = []
        dao.get_all_artists.return_value = []
        dao.get_all_genres.return_value = []

        cache = avalon.cache.IdLookupCache(dao).reload()

        assert None is cache.get_album_id('Bad Religion')

    def test_get_artist_id_case_insensitive(self):
        """Test that we can translate an artist name to ID in a case insensitive fashion"""
        model1 = avalon.models.Artist()
        model1.id = uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd")
        model1.name = 'Bad Religion'

        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = []
        dao.get_all_artists.return_value = [model1]
        dao.get_all_genres.return_value = []

        cache = avalon.cache.IdLookupCache(dao).reload()

        assert uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd") == \
               cache.get_artist_id('BaD RELIGION')

    def test_get_genre_id_exists(self):
        """Test that we can translate an genre name to ID"""
        model1 = avalon.models.Genre()
        model1.id = uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5")
        model1.name = 'Punk'

        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = []
        dao.get_all_artists.return_value = []
        dao.get_all_genres.return_value = [model1]

        cache = avalon.cache.IdLookupCache(dao).reload()

        assert uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5") == \
               cache.get_genre_id('Punk')

    def test_get_genre_id_does_not_exist(self):
        """Test that an genre that does not exist returns None"""
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = []
        dao.get_all_artists.return_value = []
        dao.get_all_genres.return_value = []

        cache = avalon.cache.IdLookupCache(dao).reload()

        assert None is cache.get_album_id('Punks')

    def test_get_genre_id_case_insensitive(self):
        """Test that we can translate an genre name to ID in a case insensitive fashion"""
        model1 = avalon.models.Genre()
        model1.id = uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5")
        model1.name = 'Punk'

        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = []
        dao.get_all_artists.return_value = []
        dao.get_all_genres.return_value = [model1]

        cache = avalon.cache.IdLookupCache(dao).reload()

        assert uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5") == \
               cache.get_genre_id('PUNK')

    def test_reload_calls_dao_methods(self):
        """Ensure that the .reload() method calls the DAO methods again"""
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = []
        dao.get_all_artists.return_value = []
        dao.get_all_genres.return_value = []

        avalon.cache.IdLookupCache(dao).reload()


class TestIdNameStore(object):
    def test_get_by_id(self):
        model1 = avalon.models.Album()
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = 'Dookie'

        model2 = avalon.models.Album()
        model2.id = uuid.UUID("b3c204e4-445d-5812-9366-28de6770c4e1")
        model2.name = 'Insomniac'

        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = [model1, model2]

        cache = avalon.cache.AlbumStore(dao).reload()

        res = cache.get_by_id(uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a"))
        assert 1 == len(res)

        for dookie in res:
            assert 'Dookie' == dookie.name

    def test_get_all(self):
        model1 = avalon.models.Album()
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = 'Dookie'

        model2 = avalon.models.Album()
        model2.id = uuid.UUID("b3c204e4-445d-5812-9366-28de6770c4e1")
        model2.name = 'Insomniac'

        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_albums.return_value = [model1, model2]

        names = set(['Dookie', 'Insomniac'])
        cache = avalon.cache.AlbumStore(dao).reload()

        res = cache.get_all()
        assert 2 == len(res)

        for album in res:
            assert album.name in names


class TestTrackStore(object):

    def setup(self):
        album = avalon.models.Album()
        album.id = uuid.UUID("350c49d9-fa38-585a-a0d9-7343c8b910ed")
        album.name = 'Ruiner'

        artist = avalon.models.Artist()
        artist.id = uuid.UUID("aa143f55-65e3-59f3-a1d8-36eac7024e86")
        artist.name = 'A Wilhelm Scream'

        genre = avalon.models.Genre()
        genre.id = uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5")
        genre.name = 'Punk'

        song = avalon.models.Track()
        song.id = uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29")
        song.name = 'The Pool'
        song.length = 150
        song.track = 3
        song.year = 2005

        song.album_id = album.id
        song.artist_id = artist.id
        song.genre_id = genre.id

        song.album = album
        song.artist = artist
        song.genre = genre

        self.song = song

    def test_get_by_album(self):
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_tracks.return_value = [self.song]

        cache = avalon.cache.TrackStore(dao).reload()
        songs = cache.get_by_album(uuid.UUID("350c49d9-fa38-585a-a0d9-7343c8b910ed"))

        for song in songs:
            assert uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29") == song.id

    def test_get_by_album_missing(self):
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_tracks.return_value = [self.song]

        cache = avalon.cache.TrackStore(dao).reload()
        songs = cache.get_by_album(uuid.UUID('daa612e8-daa8-49a0-8b14-6ee85720fb1c'))
        assert 0 == len(songs)

    def test_get_by_artist(self):
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_tracks.return_value = [self.song]

        cache = avalon.cache.TrackStore(dao).reload()
        songs = cache.get_by_artist(uuid.UUID("aa143f55-65e3-59f3-a1d8-36eac7024e86"))

        for song in songs:
            assert uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29") == song.id

    def test_get_by_artist_missing(self):
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_tracks.return_value = [self.song]

        cache = avalon.cache.TrackStore(dao).reload()
        songs = cache.get_by_artist(uuid.UUID('a15dfab4-75e6-439f-b621-5a3a9cf905d2'))
        assert 0 == len(songs)

    def test_get_by_genre(self):
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_tracks.return_value = [self.song]

        cache = avalon.cache.TrackStore(dao).reload()
        songs = cache.get_by_genre(uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5"))

        for song in songs:
            assert uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29") == song.id

    def test_get_by_genre_missing(self):
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_tracks.return_value = [self.song]

        cache = avalon.cache.TrackStore(dao).reload()
        songs = cache.get_by_genre(uuid.UUID('cf16d2d9-35da-4c2f-9f35-e52fb952864e'))
        assert 0 == len(songs)

    def test_get_by_id(self):
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_tracks.return_value = [self.song]

        cache = avalon.cache.TrackStore(dao).reload()
        songs = cache.get_by_id(uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29"))

        for song in songs:
            assert uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29") == song.id

    def test_get_by_id_missing(self):
        dao = mock.Mock(spec=avalon.models.ReadOnlyDao)
        dao.get_all_tracks.return_value = [self.song]

        cache = avalon.cache.TrackStore(dao).reload()
        songs = cache.get_by_id(uuid.UUID('72e2e340-fabc-4712-aa26-8a8f122999e8'))
        assert 0 == len(songs)
