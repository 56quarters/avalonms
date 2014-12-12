# -*- coding: utf-8 -*-
#

from __future__ import absolute_import, unicode_literals
import uuid

import pytest
import mock
import avalon.cache
import avalon.ids
import avalon.models
import avalon.tags.insert


class DummySession(object):
    """Allow tests to mock the needed methods from an
    SQLAlchemy session object.
    """

    def query(self, cls):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

    def add(self, val):
        pass

    def add_all(self, values):
        pass

    def flush(self, objects=None):
        pass


class DummyQuery(object):
    """Allow tests to mock the needed methods from an
    SQLAlchemy query object.
    """

    def delete(self):
        pass


class MockTag(object):
    """Allow tests to mock the result of calling a audio tag
    implementation.
    """

    def __init__(self):
        self.path = None
        self.album = None
        self.artist = None
        self.genre = None
        self.title = None
        self.track = None
        self.year = None
        self.length = None


class ListMatcher(object):
    """Matcher that ensures two lists have the same contents, regardless of order"""

    def __init__(self, val):
        self._val = val

    def __eq__(self, other):
        if len(self._val) != len(other):
            return False
        for val in self._val:
            if 0 == other.count(val):
                return False
        return True


class TestCleaner(object):
    def test_clean_success(self):
        """Test that the happy path works properly."""
        session = mock.Mock(spec=DummySession)
        query = mock.Mock(spec=DummyQuery)

        session.query.return_value = query

        clean = avalon.tags.insert.Cleaner(session)
        clean.clean_type(avalon.models.Album)


class TestTrackFieldLoader(object):
    def test_insert_invalid_attribute_raises_error(self):
        """Test that a call to insert a bogus tag field results in
        the expected attribute error.
        """
        tag = MockTag()
        tag.path = '/home/something/music/song.flac'
        tag.album = 'True North'
        tag.artist = 'Bad Religion'
        tag.genre = 'Punk'
        tag.length = 115
        tag.title = 'True North'
        tag.track = 1
        tag.year = 2013

        session = mock.Mock(spec=DummySession)
        model_cls = mock.Mock()
        id_gen = mock.Mock()

        inserter = avalon.tags.insert.TrackFieldLoader(session, [tag])

        with pytest.raises(AttributeError):
            inserter.insert(model_cls, id_gen, 'blah')

    def test_insert_invalid_attribute_error_unicode_path(self):
        """Test that we don't encounter unicode related errors when
        trying to handle expected errors during insert for tracks with
        non-ascii characters in the field path.
        """
        tag = MockTag()
        tag.path = '/home/something/music/¡Tré!/song.flac'
        tag.album = '¡Tré!'
        tag.artist = 'Green Day'
        tag.genre = 'Punk'
        tag.length = 148
        tag.title = 'Amanda'
        tag.track = 8
        tag.year = 2012

        session = mock.Mock(spec=DummySession)
        model_cls = mock.Mock()
        id_gen = mock.Mock()

        inserter = avalon.tags.insert.TrackFieldLoader(session, [tag])

        with pytest.raises(AttributeError):
            inserter.insert(model_cls, id_gen, 'blah')

    def test_insert_duplicate_ids_one_insert(self):
        """Test that fields are deduplicated based on their UUIDs
        when being inserted into the database.
        """
        tag1 = MockTag()
        tag1.path = '/home/something/music/¡Tré!/song.flac'
        tag1.album = '¡Tré!'
        tag1.artist = 'Green Day'
        tag1.genre = 'Punk'
        tag1.length = 148
        tag1.title = 'Amanda'
        tag1.track = 8
        tag1.year = 2012

        tag2 = MockTag()
        tag2.path = '/home/something/music/song.flac'
        tag2.album = 'True North'
        tag2.artist = 'Bad Religion'
        tag2.genre = 'Punk'
        tag2.length = 115
        tag2.title = 'True North'
        tag2.track = 1
        tag2.year = 2013

        session = mock.Mock(spec=DummySession)
        id_gen = mock.Mock()
        model_cls = mock.Mock()
        model1 = mock.Mock(spec=avalon.models.Album)
        model2 = mock.Mock(spec=avalon.models.Album)

        model_cls.side_effect = [model1, model2]
        id_gen.side_effect = ['422070a0-16a8-5c14-a4bf-a9fb82504894', 'ebaa57ed-4b57-5a1e-8295-16a3a20a2c42']

        inserter = avalon.tags.insert.TrackFieldLoader(
            session, [tag1, tag2])

        inserter.insert(model_cls, id_gen, 'album')
        session.add_all.assert_called_once_with(ListMatcher([model1, model2]))

    def test_insert_success(self):
        """Test the happy path for inserting a tag field."""
        tag = MockTag()
        tag.path = '/home/something/music/¡Tré!/song.flac'
        tag.album = '¡Tré!'
        tag.artist = 'Green Day'
        tag.genre = 'Punk'
        tag.length = 148
        tag.title = 'Amanda'
        tag.track = 8
        tag.year = 2012

        session = mock.Mock(spec=DummySession)
        id_gen = mock.Mock()
        model_cls = mock.Mock()
        model = mock.Mock(spec=avalon.models.Album)

        model_cls.return_value = model
        id_gen.return_value = '422070a0-16a8-5c14-a4bf-a9fb82504894'

        inserter = avalon.tags.insert.TrackFieldLoader(session, [tag])
        inserter.insert(model_cls, id_gen, 'album')

        session.add_all.assert_called_once_with([model])


class TestTrackLoader(object):
    def test_attribute_ids_lookup_by_tag_values(self):
        """Test that IDs are looked up in the ID cache based on
        values from the tag being inserted.
        """
        ruiner = uuid.UUID('350c49d9-fa38-585a-a0d9-7343c8b910ed')
        a_wilhelm_scream = uuid.UUID('aa143f55-65e3-59f3-a1d8-36eac7024e86')
        hardcore = uuid.UUID('54cde78b-6d4b-5634-a666-cb7fa674c73f')

        tag = MockTag()
        tag.path = '/home/something/music/song.flac'
        tag.album = 'Ruiner'
        tag.artist = 'A Wilhelm Scream'
        tag.genre = 'Hardcore'
        tag.length = 150
        tag.title = 'The Soft Sell'
        tag.track = 4
        tag.year = 2005

        cache = mock.Mock(spec=avalon.cache.IdLookupCache)
        cache.get_album_id.return_value = ruiner
        cache.get_artist_id.return_value = a_wilhelm_scream
        cache.get_genre_id('Hardcore').return_value = hardcore

        session = mock.Mock(spec=DummySession)
        id_gen = mock.Mock()
        model_cls = mock.Mock()
        model = mock.Mock(spec=avalon.models.Track)

        model_cls.return_value = model
        id_gen.return_value = uuid.UUID('450b3e88-01e0-537a-80cd-c8692c903c76')

        inserter = avalon.tags.insert.TrackLoader(session, [tag], cache)
        inserter.insert(model_cls, id_gen)

        session.add_all.assert_called_once_with([model])
