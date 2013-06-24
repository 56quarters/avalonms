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
        model1 = self.mox.CreateMock(avalon.models.Album)
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = u'Dookie'

        model2 = self.mox.CreateMock(avalon.models.Album)
        model2.id = uuid.UUID("b3c204e4-445d-5812-9366-28de6770c4e1")
        model2.name = u'Insomniac'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([model1, model2])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a") == cache.get_album_id(u'Dookie')
        assert uuid.UUID("b3c204e4-445d-5812-9366-28de6770c4e1") == cache.get_album_id(u'Insomniac')

    def test_get_album_id_does_not_exist(self):
        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert None is cache.get_album_id(u'Dookie')

    def test_get_album_id_case_insensitive(self):
        model1 = self.mox.CreateMock(avalon.models.Album)
        model1.id = uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a")
        model1.name = u'Dookie'

        model2 = self.mox.CreateMock(avalon.models.Album)
        model2.id = uuid.UUID("b3c204e4-445d-5812-9366-28de6770c4e1")
        model2.name = u'Insomniac'

        dao = self.mox.CreateMock(avalon.cache.ReadOnlyDao)
        dao.get_all_albums().AndReturn([model1, model2])
        dao.get_all_artists().AndReturn([])
        dao.get_all_genres().AndReturn([])

        self.mox.ReplayAll()

        cache = avalon.cache.IdLookupCache(dao)

        assert uuid.UUID("2d24515c-a459-552a-b022-e85d1621425a") == cache.get_album_id(u'DOOKIE')
        assert uuid.UUID("b3c204e4-445d-5812-9366-28de6770c4e1") == cache.get_album_id(u'INSOMNIAC')


