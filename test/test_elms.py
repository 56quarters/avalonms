# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals
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
    def setup(self):
        self.artist_model = DummyIdNameModel()
        self.artist_model.id = uuid.uuid4()
        self.artist_model.name = 'Bad Religion'

    def test_from_model_same_values(self):
        artist_elm = avalon.elms.id_name_elm_from_model(self.artist_model)

        assert artist_elm.id == self.artist_model.id
        assert artist_elm.name == self.artist_model.name

    def test_from_model_immutable(self):
        artist_elm = avalon.elms.id_name_elm_from_model(self.artist_model)

        with pytest.raises(AttributeError):
            artist_elm.name = 'Something'


class TestTrackElm(object):
    def setup(self):
        self.artist_model = DummyIdNameModel()
        self.artist_model.id = uuid.uuid4()
        self.artist_model.name = 'Bad Religion'

        self.album_model = DummyIdNameModel()
        self.album_model.id = uuid.uuid4()
        self.album_model.name = 'Against The Grain'

        self.genre_model = DummyIdNameModel()
        self.genre_model.id = uuid.uuid4()
        self.genre_model.name = 'Punk'

        self.track_model = DummyTrackModel()
        self.track_model.id = uuid.uuid4()
        self.track_model.name = 'Walk Away'
        self.track_model.length = 112
        self.track_model.track = 17
        self.track_model.year = 1991
        self.track_model.album = self.album_model
        self.track_model.album_id = self.album_model.id
        self.track_model.artist = self.artist_model
        self.track_model.artist_id = self.artist_model.id
        self.track_model.genre = self.genre_model
        self.track_model.genre_id = self.genre_model.id

    def test_from_model_same_values(self):
        track_elm = avalon.elms.track_elm_from_model(self.track_model)

        assert track_elm.id == self.track_model.id
        assert track_elm.name == self.track_model.name
        assert track_elm.length == self.track_model.length
        assert track_elm.track == self.track_model.track
        assert track_elm.year == self.track_model.year

        assert track_elm.album == self.album_model.name
        assert track_elm.album_id == self.track_model.album_id
        assert track_elm.artist == self.artist_model.name
        assert track_elm.artist_id == self.track_model.artist_id
        assert track_elm.genre == self.genre_model.name
        assert track_elm.genre_id == self.track_model.genre_id

    def test_from_model_immutable(self):
        track_elm = avalon.elms.track_elm_from_model(self.track_model)

        with pytest.raises(AttributeError):
            track_elm.id = uuid.uuid4()
