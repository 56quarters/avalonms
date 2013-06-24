# -*- coding: utf-8 -*-
#

import uuid

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

        assert uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a") == cache.get_album_id(u'Dookie')
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

        assert uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a") == cache.get_album_id(u'DOOKIE')
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

        assert uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd") == cache.get_artist_id(u'Bad Religion')
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

        assert uuid.UUID("5cede078-e88e-5929-b8e1-cfda7992b8fd") == cache.get_artist_id(u'BaD RELIGION')
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

        assert uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5") == cache.get_genre_id(u'Punk')
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

        assert uuid.UUID("8794d7b7-fff3-50bb-b1f1-438659e05fe5") == cache.get_genre_id(u'PUNK')
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

        res = cache.by_id(uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a"))
        assert 1 == len(res)

        for dookie in res:
            assert u'Dookie' == dookie.name
        self.mox.VerifyAll()

    def test_all(self):
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

        res = cache.all()
        assert 2 == len(res)

        for album in res:
            assert album.name in names
        self.mox.VerifyAll()

