# -*- coding: utf-8 -*-
#


from __future__ import absolute_import, unicode_literals
import uuid

import pytest
import mock
from avalon import six
import avalon.cache
import avalon.compat
import avalon.elms
import avalon.web.request
import avalon.web.search
import avalon.web.services


class DummyRequest(object):
    def __init__(self):
        self.args = {}


@pytest.fixture
def albums():
    store = mock.Mock(spec=avalon.cache.AlbumStore)
    store.__len__ = lambda self: 0
    return store


@pytest.fixture
def artists():
    store = mock.Mock(spec=avalon.cache.ArtistStore)
    store.__len__ = lambda self: 0
    return store


@pytest.fixture
def genres():
    store = mock.Mock(spec=avalon.cache.GenreStore)
    store.__len__ = lambda self: 0
    return store


@pytest.fixture
def tracks():
    store = mock.Mock(spec=avalon.cache.TrackStore)
    store.__len__ = lambda self: 0
    return store


@pytest.fixture
def search():
    store = mock.Mock(spec=avalon.web.search.AvalonTextSearch)
    store.__len__ = lambda self: 0
    return store


@pytest.fixture
def id_cache():
    return mock.Mock(spec=avalon.cache.IdLookupCache)


@pytest.fixture
def id_name_elms():
    return frozenset([
        avalon.elms.IdNameElm(
            id=uuid.UUID(avalon.compat.to_uuid_input('f27ed1e2-3626-4fb8-b2a6-e012603b06e4')),
            name='Dummy Value 1')
    ])


@pytest.fixture
def track_elms():
    return frozenset([
        avalon.elms.TrackElm(
            id=uuid.UUID(avalon.compat.to_uuid_input('cd296eb6-0f7a-4086-a5ff-bc5ee0aee172')),
            name='Dummy Track 1',
            length=128,
            track=12,
            year=1994,
            album='Dummy Album',
            album_id=uuid.UUID(avalon.compat.to_uuid_input('dee19f37-d932-4159-ba1f-ea0a0b968ccd')),
            artist='Dummy Artist',
            artist_id=uuid.UUID(avalon.compat.to_uuid_input('de04d6e1-8391-433e-95ae-e12a5422edeb')),
            genre='Dummy Genre',
            genre_id=uuid.UUID(avalon.compat.to_uuid_input('51755b6f-e1bd-4255-aeb9-bb1ef63875c9')))
    ])


@pytest.fixture
def service_config(albums, artists, genres, tracks, search, id_cache):
    config = avalon.web.services.AvalonMetadataServiceConfig()
    config.album_store = albums
    config.artist_store = artists
    config.genre_store = genres
    config.track_store = tracks
    config.search = search
    config.id_cache = id_cache
    return config


@pytest.fixture
def request():
    return DummyRequest()


def test_intersection_with_empty_set():
    set1 = set(['foo', 'bar'])
    set2 = set(['foo'])
    set3 = set()

    res = avalon.web.services.intersection([set1, set2, set3])
    assert 0 == len(res), 'Expected empty set of common results'


def test_intersection_no_overlap():
    set1 = set(['foo', 'bar'])
    set2 = set(['baz'])
    set3 = set(['bing'])

    res = avalon.web.services.intersection([set1, set2, set3])
    assert 0 == len(res), 'Expected empty set of common results'


def test_intersection_with_overlap():
    set1 = set(['foo', 'bar'])
    set2 = set(['foo', 'baz'])
    set3 = set(['bing', 'foo'])

    res = avalon.web.services.intersection([set1, set2, set3])
    assert 1 == len(res), 'Expected set of one common result'


class TestAvalonMetadataService(object):
    def test_reload(self, service_config):
        """Ensure that reloading the service reloads each contained store."""
        service = avalon.web.services.AvalonMetadataService(service_config)
        service.reload()

        assert service_config.track_store.reload.called, \
            'Expected track store reload to be called'

        assert service_config.album_store.reload.called, \
            'Expected album store reload to be called'

        assert service_config.artist_store.reload.called, \
            'Expected artist store reload to be called'

        assert service_config.genre_store.reload.called, \
            'Expected genre store reload to be called'

        assert service_config.search.reload.called, \
            'Expected search trie reload to be called'

        assert service_config.id_cache.reload.called, \
            'Expected ID cache reload to be called'

    def test_get_albums_no_params(self, id_name_elms, service_config, request):
        """Test that we can fetch all albums available."""
        service_config.album_store.get_all.return_value = id_name_elms
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_albums(params)

        assert results == id_name_elms, 'Expected all albums returned'

    def test_get_albums_query_param(self, id_name_elms, service_config, request):
        """Test that we can fetch a subset of albums based on a query param."""
        service_config.search.search_albums.return_value = id_name_elms
        request.args['query'] = 'Dummy'
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_albums(params)

        assert results == id_name_elms, 'Expected matching albums returned'

    def test_get_artists_no_params(self, id_name_elms, service_config, request):
        """Test that we can fetch all artists available."""
        service_config.artist_store.get_all.return_value = id_name_elms
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_artists(params)

        assert results == id_name_elms, 'Expected all artists returned'

    def test_get_artists_query_param(self, id_name_elms, service_config, request):
        """Test that we can fetch a subset of artists based on a query param."""
        service_config.search.search_artists.return_value = id_name_elms
        request.args['query'] = 'Dummy'
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_artists(params)

        assert results == id_name_elms, 'Expected matching artists returned'

    def test_get_genres_no_params(self, id_name_elms, service_config, request):
        """Test that we can fetch all genres available."""
        service_config.genre_store.get_all.return_value = id_name_elms
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_genres(params)

        assert results == id_name_elms, 'Expected all genres returned'

    def test_get_genres_query_param(self, id_name_elms, service_config, request):
        """Test that we can fetch a subset of genres based on a query param."""
        service_config.search.search_genres.return_value = id_name_elms
        request.args['query'] = 'Dummy'
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_genres(params)

        assert results == id_name_elms, 'Expected matching genres returned'

    def test_get_songs_no_params(self, track_elms, service_config, request):
        """Test that we can fetch all tracks when the params are empty."""
        service_config.track_store.get_all.return_value = track_elms
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_songs(params)

        assert results == track_elms, 'Expected all tracks returned'


    def test_get_songs_none_params(self, track_elms, service_config):
        """Test that we can fetch all tracks when the params are omitted."""
        service_config.track_store.get_all.return_value = track_elms
        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_songs(None)

        assert results == track_elms, 'Expected all tracks returned'

    def test_get_songs_by_query(self, track_elms, service_config, request):
        """Test that we can fetch tracks by text matching."""
        service_config.search.search_tracks.return_value = track_elms
        request.args['query'] = 'Dummy'
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_songs(params)

        assert results == track_elms, 'Expected matching tracks returned'

    def test_get_songs_by_album(self, track_elms, service_config, request):
        """Test that we can fetch tracks by exact album."""
        album_id = uuid.UUID(avalon.compat.to_uuid_input('f83fdec7-510f-44a5-87dc-61832669a582'))
        service_config.track_store.get_by_album.return_value = track_elms
        service_config.id_cache.get_album_id.return_value = album_id
        request.args['album'] = 'Album'
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_songs(params)

        assert results == track_elms, 'Expected matching tracks returned'
        service_config.track_store.get_by_album.assert_called_with(album_id)

    def test_get_songs_by_artist(self, track_elms, service_config, request):
        """Test that we can fetch tracks by exact artist."""
        artist_id = uuid.UUID(avalon.compat.to_uuid_input('2221930a-f28d-44ed-856b-c84b35f76713'))
        service_config.track_store.get_by_artist.return_value = track_elms
        service_config.id_cache.get_artist_id.return_value = artist_id
        request.args['artist'] = 'Artist'
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_songs(params)

        assert results == track_elms, 'Expected matching tracks returned'
        service_config.track_store.get_by_artist.assert_called_with(artist_id)

    def test_get_songs_by_genre(self, track_elms, service_config, request):
        """Test that we can fetch tracks by exact genre."""
        genre_id = uuid.UUID(avalon.compat.to_uuid_input('c12d2a49-d086-43d6-953d-b870deb24228'))
        service_config.track_store.get_by_genre.return_value = track_elms
        service_config.id_cache.get_genre_id.return_value = genre_id
        request.args['genre'] = 'Genre'
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_songs(params)

        assert results == track_elms, 'Expected matching tracks returned'
        service_config.track_store.get_by_genre.assert_called_with(genre_id)

    def test_get_songs_by_album_id(self, track_elms, service_config, request):
        """Test that we can fetch tracks by album UUID."""
        album_id = uuid.UUID(avalon.compat.to_uuid_input('37cac253-2bca-4a3a-be9f-2ac655e04ad8'))
        service_config.track_store.get_by_album.return_value = track_elms
        request.args['album_id'] = six.text_type(album_id)
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_songs(params)

        assert results == track_elms, 'Expected matching tracks returned'
        service_config.track_store.get_by_album.assert_called_with(album_id)

    def test_get_songs_by_artist_id(self, track_elms, service_config, request):
        """Test that we can fetch tracks by artist UUID."""
        artist_id = uuid.UUID(avalon.compat.to_uuid_input('75d590d1-9f3d-462d-8264-0d16af227860'))
        service_config.track_store.get_by_artist.return_value = track_elms
        request.args['artist_id'] = six.text_type(artist_id)
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_songs(params)

        assert results == track_elms, 'Expected matching tracks returned'
        service_config.track_store.get_by_artist.assert_called_with(artist_id)

    def test_get_songs_by_genre_id(self, track_elms, service_config, request):
        """Test that we can fetch tracks by genre UUID."""
        genre_id = uuid.UUID(avalon.compat.to_uuid_input('26ce4d6b-af97-45a6-b7f6-d5c1cbbfd6b1'))
        service_config.track_store.get_by_genre.return_value = track_elms
        request.args['genre_id'] = six.text_type(genre_id)
        params = avalon.web.request.Parameters(request)

        service = avalon.web.services.AvalonMetadataService(service_config)
        results = service.get_songs(params)

        assert results == track_elms, 'Expected matching tracks returned'
        service_config.track_store.get_by_genre.assert_called_with(genre_id)
