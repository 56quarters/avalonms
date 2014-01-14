# -*- coding: utf-8 -*-
#

import uuid

# TOOD: Replace mox with mock lib, pypi for python 2 - 3.2, stdlib for python 3.3
import mox
import pytest

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
    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_get_album_id_exists(self):
        """Test that we can translate an album name to ID"""
        model1 = self.mox.CreateMock(avalon.models.Album)
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = u'Dookie'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([model1])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a") == \
               cache.get_album_id(u'Dookie')
        self.mox.VerifyAll()

    def test_get_album_id_does_not_exist(self):
        """Test that an album that does not exist returns None"""
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert None is cache.get_album_id(u'Dookie')
        self.mox.VerifyAll()

    def test_get_album_id_case_insensitive(self):
        """Test that we can translate an album name to ID in a case insensitive fasion"""
        model1 = self.mox.CreateMock(avalon.models.Album)
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = u'Dookie'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([model1])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a") == \
               cache.get_album_id(u'DOOKIE')
        self.mox.VerifyAll()

    def test_get_artist_id_exists(self):
        """Test that we can translate an artist name to ID"""
        model1 = self.mox.CreateMock(avalon.models.Album)
        model1.id = uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd")
        model1.name = u'Bad Religion'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([model1])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd") == \
               cache.get_artist_id(u'Bad Religion')
        self.mox.VerifyAll()

    def test_get_artist_id_does_not_exist(self):
        """Test that an artist that does not exist returns None"""
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert None is cache.get_album_id(u'Bad Religion')
        self.mox.VerifyAll()

    def test_get_artist_id_case_insensitive(self):
        """Test that we can translate an artist name to ID in a case insensitive fasion"""
        model1 = self.mox.CreateMock(avalon.models.Artist)
        model1.id = uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd")
        model1.name = u'Bad Religion'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([model1])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd") == \
               cache.get_artist_id(u'BaD RELIGION')
        self.mox.VerifyAll()

    def test_get_genre_id_exists(self):
        """Test that we can translate an genre name to ID"""
        model1 = self.mox.CreateMock(avalon.models.Genre)
        model1.id = uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5")
        model1.name = u'Punk'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([model1])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5") == \
               cache.get_genre_id(u'Punk')
        self.mox.VerifyAll()

    def test_get_genre_id_does_not_exist(self):
        """Test that an genre that does not exist returns None"""
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert None is cache.get_album_id(u'Punks')
        self.mox.VerifyAll()

    def test_get_genre_id_case_insensitive(self):
        """Test that we can translate an genre name to ID in a case insensitive fasion"""
        model1 = self.mox.CreateMock(avalon.models.Genre)
        model1.id = uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5")
        model1.name = u'Punk'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([model1])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5") == \
               cache.get_genre_id(u'PUNK')
        self.mox.VerifyAll()

    def test_reload_calls_dao_methods(self):
        """Ensure that the .reload() method calls the DAO methods again"""
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)
        cache.reload()

        self.mox.VerifyAll()


class TestIdNameStore(object):
    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_get_by_id(self):
        model1 = self.mox.CreateMock(avalon.models.Album)
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = u'Dookie'

        model2 = self.mox.CreateMock(avalon.models.Album)
        model2.id = uuid.UUID("b3c204e4-445d-5812-9366-28de6770c4e1")
        model2.name = u'Insomniac'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([model1, model2])

        self.mox.ReplayAll()

        cache = avalon.cache.AlbumStore(dao)

        res = cache.get_by_id(uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a"))
        assert 1 == len(res)

        for dookie in res:
            assert u'Dookie' == dookie.name
        self.mox.VerifyAll()

    def test_get_all(self):
        model1 = self.mox.CreateMock(avalon.models.Album)
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = u'Dookie'

        model2 = self.mox.CreateMock(avalon.models.Album)
        model2.id = uuid.UUID("b3c204e4-445d-5812-9366-28de6770c4e1")
        model2.name = u'Insomniac'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([model1, model2])

        self.mox.ReplayAll()

        names = set([u'Dookie', u'Insomniac'])
        cache = avalon.cache.AlbumStore(dao)

        res = cache.get_all()
        assert 2 == len(res)

        for album in res:
            assert album.name in names
        self.mox.VerifyAll()


class TestTrackStore(object):
    def setup_method(self, method):
        self.mox = mox.Mox()

        album = self.mox.CreateMock(avalon.models.Album)
        album.id = uuid.UUID("350c49d9-fa38-585a-a0d9-7343c8b910ed")
        album.name = u'Ruiner'

        artist = self.mox.CreateMock(avalon.models.Artist)
        artist.id = uuid.UUID("aa143f55-65e3-59f3-a1d8-36eac7024e86")
        artist.name = u'A Wilhelm Scream'

        genre = self.mox.CreateMock(avalon.models.Genre)
        genre.id = uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5")
        genre.name = u'Punk'

        song = self.mox.CreateMock(avalon.models.Track)
        song.id = uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29")
        song.name = u'The Pool'
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

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_get_by_album(self):
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_tracks().AndReturn([self.song])
        self.mox.ReplayAll()

        cache = avalon.cache.TrackStore(dao)
        songs = cache.get_by_album(uuid.UUID("350c49d9-fa38-585a-a0d9-7343c8b910ed"))

        for song in songs:
            assert uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29") == song.id

    def test_get_by_album_missing(self):
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_tracks().AndReturn([self.song])
        self.mox.ReplayAll()

        cache = avalon.cache.TrackStore(dao)
        songs = cache.get_by_album(uuid.UUID('daa612e8-daa8-49a0-8b14-6ee85720fb1c'))
        assert 0 == len(songs)

    def test_get_by_artist(self):
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_tracks().AndReturn([self.song])
        self.mox.ReplayAll()

        cache = avalon.cache.TrackStore(dao)
        songs = cache.get_by_artist(uuid.UUID("aa143f55-65e3-59f3-a1d8-36eac7024e86"))

        for song in songs:
            assert uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29") == song.id

    def test_get_by_artist_missing(self):
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_tracks().AndReturn([self.song])
        self.mox.ReplayAll()

        cache = avalon.cache.TrackStore(dao)
        songs = cache.get_by_artist(uuid.UUID('a15dfab4-75e6-439f-b621-5a3a9cf905d2'))
        assert 0 == len(songs)

    def test_get_by_genre(self):
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_tracks().AndReturn([self.song])
        self.mox.ReplayAll()

        cache = avalon.cache.TrackStore(dao)
        songs = cache.get_by_genre(uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5"))

        for song in songs:
            assert uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29") == song.id

    def test_get_by_genre_missing(self):
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_tracks().AndReturn([self.song])
        self.mox.ReplayAll()

        cache = avalon.cache.TrackStore(dao)
        songs = cache.get_by_genre(uuid.UUID('cf16d2d9-35da-4c2f-9f35-e52fb952864e'))
        assert 0 == len(songs)

    def test_get_by_id(self):
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_tracks().AndReturn([self.song])
        self.mox.ReplayAll()

        cache = avalon.cache.TrackStore(dao)
        songs = cache.get_by_id(uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29"))

        for song in songs:
            assert uuid.UUID("ca2e8303-69d7-53ec-907e-2f111103ba29") == song.id

    def test_get_by_id_missing(self):
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_tracks().AndReturn([self.song])
        self.mox.ReplayAll()

        cache = avalon.cache.TrackStore(dao)
        songs = cache.get_by_id(uuid.UUID('72e2e340-fabc-4712-aa26-8a8f122999e8'))
        assert 0 == len(songs)

