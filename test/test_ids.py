# -*- coding: utf-8 -*-
#

import uuid

import avalon.ids


class TestAlbumIds(object):
    def test_get_album_id_lowercase(self):
        album_title = u'career suicide'
        generated = avalon.ids.get_album_id(album_title)
        expected = uuid.UUID('763d6b20-7620-561f-9d11-702c5d02406d')
        assert expected == generated

    def test_get_album_id_titlecase(self):
        album_title = u'Career Suicide'
        generated = avalon.ids.get_album_id(album_title)
        expected = uuid.UUID('763d6b20-7620-561f-9d11-702c5d02406d')
        assert expected == generated


class TestArtistIds(object):
    def test_get_artist_id_lowercase(self):
        artist_name = u'operation ivy'
        generated = avalon.ids.get_artist_id(artist_name)
        expected = uuid.UUID('680643dc-1b65-56ec-b2fc-bdc9703ab9a2')
        assert expected == generated

    def test_get_artist_id_titlecase(self):
        artist_name = u'Operation Ivy'
        generated = avalon.ids.get_artist_id(artist_name)
        expected = uuid.UUID('680643dc-1b65-56ec-b2fc-bdc9703ab9a2')
        assert expected == generated


class TestGenreIds(object):
    def test_get_genre_id_lowercase(self):
        genre = u'ska'
        generated = avalon.ids.get_genre_id(genre)
        expected = uuid.UUID('62d4db4c-160c-52e4-8c47-bf2e7b412ca2')
        assert expected == generated

    def test_get_genre_id_titlecase(self):
        genre = u'Ska'
        generated = avalon.ids.get_genre_id(genre)
        expected = uuid.UUID('62d4db4c-160c-52e4-8c47-bf2e7b412ca2')
        assert expected == generated


class TestTrackIds(object):
    def test_get_track_id_all_lowercase(self):
        path = u'/home/some/path/file.mp3'
        generated = avalon.ids.get_track_id(path)
        expected = uuid.UUID('c522c566-ba2b-573e-b13f-f526edba1941')
        assert expected == generated

    def test_get_track_id_mixed_case(self):
        path = u'/home/some/path/File.mp3'
        generated = avalon.ids.get_track_id(path)
        expected = uuid.UUID('e10a78c2-db14-55f0-85ff-4b24140ff776')
        assert expected == generated

    def test_get_track_id_case_sensitive(self):
        generated1 = avalon.ids.get_track_id(u'/home/some/Path/File.mp3')
        generated2 = avalon.ids.get_track_id(u'/home/some/path/file.mp3')
        assert generated1 != generated2

