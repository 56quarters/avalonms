# -*- coding: utf-8 -*-
#

import uuid

import pytest

import avalon.elms


class DummyTrackModel(object):
    def __init__(self):
        self.id = None
        self.name = None
        self.length = None
        self.track = None
        self.year = None
        self.album = None
        self.album_id = None
        self.artist = None
        self.artist_id = None
        self.genre = None
        self.genre_id = None


class DummyIdNameModel(object):
    def __init__(self):
        self.id = None
        self.name = None


class TestIdNameElm(object):
    def test_from_model_same_values(self):
        artist_model = DummyIdNameModel()
        artist_model.id = uuid.uuid4()
        artist_model.name = u'Bad Religion'

        artist_elm = avalon.elms.IdNameElm.from_model(artist_model)

        assert artist_elm.id == artist_model.id
        assert artist_elm.name == artist_model.name

    def test_from_model_immutable(self):
        artist_model = DummyIdNameModel()
        artist_model.id = uuid.uuid4()
        artist_model.name = u'Bad Religion'

        artist_elm = avalon.elms.IdNameElm.from_model(artist_model)

        with pytest.raises(AttributeError):
            artist_elm.id = uuid.uuid4()

        with pytest.raises(AttributeError):
            artist_elm.name = u'Something'


class TestTrackElm(object):
    def test_from_model_same_values(self):
        artist_model = DummyIdNameModel()
        artist_model.id = uuid.uuid4()
        artist_model.name = u'Bad Religion'

        album_model = DummyIdNameModel()
        album_model.id = uuid.uuid4()
        album_model.name = u'Against The Grain'

        genre_model = DummyIdNameModel()
        genre_model.id = uuid.uuid4()
        genre_model.name = u'Punk'

        track_model = DummyTrackModel()
        track_model.id = uuid.uuid4()
        track_model.name = u'Walk Away'
        track_model.length = 112
        track_model.track = 17
        track_model.year = 1991
        track_model.album = album_model
        track_model.album_id = album_model.id
        track_model.artist = artist_model
        track_model.artist_id = artist_model.id
        track_model.genre = genre_model
        track_model.genre_id = genre_model.id

        track_elm = avalon.elms.TrackElm.from_model(track_model)

        assert track_elm.id == track_model.id
        assert track_elm.name == track_model.name
        assert track_elm.length == track_model.length
        assert track_elm.track == track_model.track
        assert track_elm.year == track_model.year

        assert track_elm.album == album_model.name
        assert track_elm.album_id == track_model.album_id
        assert track_elm.artist == artist_model.name
        assert track_elm.artist_id == track_model.artist_id
        assert track_elm.genre == genre_model.name
        assert track_elm.genre_id == track_elm.genre_id

    def test_from_model_immutable(self):
        artist_model = DummyIdNameModel()
        artist_model.id = uuid.uuid4()
        artist_model.name = u'Bad Religion'

        album_model = DummyIdNameModel()
        album_model.id = uuid.uuid4()
        album_model.name = u'Against The Grain'

        genre_model = DummyIdNameModel()
        genre_model.id = uuid.uuid4()
        genre_model.name = u'Punk'

        track_model = DummyTrackModel()
        track_model.id = uuid.uuid4()
        track_model.name = u'Walk Away'
        track_model.length = 112
        track_model.track = 17
        track_model.year = 1991
        track_model.album = album_model
        track_model.album_id = album_model.id
        track_model.artist = artist_model
        track_model.artist_id = artist_model.id
        track_model.genre = genre_model
        track_model.genre_id = genre_model.id

        track_elm = avalon.elms.TrackElm.from_model(track_model)

        with pytest.raises(AttributeError):
            track_elm.length = 1

        with pytest.raises(AttributeError):
            track_elm.id = uuid.uuid4()
