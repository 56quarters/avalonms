# -*- coding: utf-8 -*-
#

import uuid

# TOOD: Replace mox with mock lib, pypi for python 2 - 3.2, stdlib for python 3.3
import mox
import pytest

import sqlalchemy.exc

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

    def close(self):
        pass

    def add_all(self, values):
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


class TestCleaner(object):

    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_clean_success(self):
        """Test that the happy path works properly."""
        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        session = self.mox.CreateMock(DummySession)
        query = self.mox.CreateMock(DummyQuery)

        session_handler.get_session().AndReturn(session)
        session.query(avalon.models.Album).AndReturn(query)
        query.delete()
        session.commit()
        session_handler.close(session)
        self.mox.ReplayAll()

        clean = avalon.tags.insert.Cleaner(session_handler)
        clean.clean_type(avalon.models.Album)
        self.mox.VerifyAll()

    def test_clean_with_error(self):
        """Test that errors during cleaning are handled correctly and
        we don't leak database connections.
        """
        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        session = self.mox.CreateMock(DummySession)
        err = sqlalchemy.exc.SQLAlchemyError()

        session_handler.get_session().AndReturn(session)
        session.query(avalon.models.Album).AndRaise(err)
        session_handler.close(session)
        self.mox.ReplayAll()

        clean = avalon.tags.insert.Cleaner(session_handler)
        with pytest.raises(sqlalchemy.exc.SQLAlchemyError):
            clean.clean_type(avalon.models.Album)
        self.mox.VerifyAll()


class TestTrackFieldLoader(object):

    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_insert_invalid_attribute_raises_error(self):
        """Test that a call to insert a bogus tag field results in
        the expected attribute error.
        """
        tag = MockTag()
        tag.path = u'/home/something/music/song.flac'
        tag.album = u'True North'
        tag.artist = u'Bad Religion'
        tag.genre = u'Punk'
        tag.length = 115
        tag.title = u'True North'
        tag.track = 1
        tag.year = 2014

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        model_cls = self.mox.CreateMockAnything(avalon.models.Album)
        id_gen = self.mox.CreateMockAnything(avalon.ids.get_album_id)

        inserter = avalon.tags.insert.TrackFieldLoader(session_handler, [tag])

        with pytest.raises(AttributeError):
            inserter.insert(model_cls, id_gen, 'blah')
        self.mox.VerifyAll()

    def test_insert_invalid_attribute_error_unicode_path(self):
        """Test that we don't encounter unicode related errors when
        trying to handle expected errors during insert for tracks with
        non-ascii characters in the field path.
        """
        tag = MockTag()
        tag.path = u'/home/something/music/¡Tré!/song.flac'
        tag.album = u'¡Tré!'
        tag.artist = u'Green Day'
        tag.genre = u'Punk'
        tag.length = 148
        tag.title = u'Amanda'
        tag.track = 8
        tag.year = 2012

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        model_cls = self.mox.CreateMockAnything(avalon.models.Album)
        id_gen = self.mox.CreateMockAnything(avalon.ids.get_album_id)

        inserter = avalon.tags.insert.TrackFieldLoader(session_handler, [tag])

        with pytest.raises(AttributeError):
            inserter.insert(model_cls, id_gen, 'blah')
        self.mox.VerifyAll()

    def test_insert_duplicate_ids_one_insert(self):
        """Test that fields are deduplicated based on their UUIDs
        when being inserted into the database.
        """
        tag1 = MockTag()
        tag1.path = u'/home/something/music/¡Tré!/song.flac'
        tag1.album = u'¡Tré!'
        tag1.artist = u'Green Day'
        tag1.genre = u'Punk'
        tag1.length = 148
        tag1.title = u'Amanda'
        tag1.track = 8
        tag1.year = 2012

        tag2 = MockTag()
        tag2.path = u'/home/something/music/song.flac'
        tag2.album = u'True North'
        tag2.artist = u'Bad Religion'
        tag2.genre = u'Punk'
        tag2.length = 115
        tag2.title = u'True North'
        tag2.track = 1
        tag2.year = 2014

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        session = self.mox.CreateMock(DummySession)
        id_gen = self.mox.CreateMockAnything(avalon.ids.get_album_id)
        model_cls = self.mox.CreateMockAnything(avalon.models.Album)
        model1 = self.mox.CreateMock(avalon.models.Album)
        model2 = self.mox.CreateMock(avalon.models.Album)

        model_cls().AndReturn(model1)
        id_gen(mox.IsA(unicode)).AndReturn('422070a0-16a8-5c14-a4bf-a9fb82504894')

        model_cls().AndReturn(model2)
        id_gen(mox.IsA(unicode)).AndReturn('ebaa57ed-4b57-5a1e-8295-16a3a20a2c42')

        session_handler.get_session().AndReturn(session)
        session.add_all(mox.Or(mox.In(model1), mox.In(model2)))
        session.commit()
        session_handler.close(session)

        self.mox.ReplayAll()

        inserter = avalon.tags.insert.TrackFieldLoader(
            session_handler, [tag1, tag2])

        inserter.insert(model_cls, id_gen, 'album')
        self.mox.VerifyAll()

    def test_insert_commit_error_session_closed(self):
        """Test that errors inserting fields do not result in
        leaking database connections.
        """
        tag = MockTag()
        tag.path = u'/home/something/music/song.flac'
        tag.album = u'True North'
        tag.artist = u'Bad Religion'
        tag.genre = u'Punk'
        tag.length = 115
        tag.title = u'True North'
        tag.track = 1
        tag.year = 2014

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        session = self.mox.CreateMock(DummySession)
        id_gen = self.mox.CreateMockAnything(avalon.ids.get_album_id)
        model_cls = self.mox.CreateMockAnything(avalon.models.Album)
        model = self.mox.CreateMock(avalon.models.Album)

        model_cls().AndReturn(model)
        id_gen(mox.IsA(unicode)).AndReturn('ebaa57ed-4b57-5a1e-8295-16a3a20a2c42')

        session_handler.get_session().AndReturn(session)
        session.add_all([model])
        session.commit().AndRaise(sqlalchemy.exc.NoSuchColumnError)
        session_handler.close(session)

        self.mox.ReplayAll()

        inserter = avalon.tags.insert.TrackFieldLoader(session_handler, [tag])

        # The error is expected, we just want to test that the
        # session is still closed when there is an insert error
        with pytest.raises(sqlalchemy.exc.NoSuchColumnError):
            inserter.insert(model_cls, id_gen, 'album')
        self.mox.VerifyAll()

    def test_insert_success(self):
        """Test the happy path for inserting a tag field."""
        tag = MockTag()
        tag.path = u'/home/something/music/¡Tré!/song.flac'
        tag.album = u'¡Tré!'
        tag.artist = u'Green Day'
        tag.genre = u'Punk'
        tag.length = 148
        tag.title = u'Amanda'
        tag.track = 8
        tag.year = 2012

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        session = self.mox.CreateMock(DummySession)
        id_gen = self.mox.CreateMockAnything(avalon.ids.get_album_id)
        model_cls = self.mox.CreateMockAnything(avalon.models.Album)
        model = self.mox.CreateMock(avalon.models.Album)

        model_cls().AndReturn(model)
        id_gen(mox.IsA(unicode)).AndReturn('422070a0-16a8-5c14-a4bf-a9fb82504894')

        session_handler.get_session().AndReturn(session)
        session.add_all([model])
        session.commit()
        session_handler.close(session)

        self.mox.ReplayAll()

        inserter = avalon.tags.insert.TrackFieldLoader(session_handler, [tag])
        inserter.insert(model_cls, id_gen, 'album')
        self.mox.VerifyAll()


class TestTrackLoader(object):

    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_attribute_ids_lookup_by_tag_values(self):
        """Test that IDs are looked up in the ID cache based on
        values from the tag being inserted.
        """
        ruiner = uuid.UUID('350c49d9-fa38-585a-a0d9-7343c8b910ed')
        a_wilhelm_scream = uuid.UUID('aa143f55-65e3-59f3-a1d8-36eac7024e86')
        hardcore = uuid.UUID('54cde78b-6d4b-5634-a666-cb7fa674c73f')

        tag = MockTag()
        tag.path = u'/home/something/music/song.flac'
        tag.album = u'Ruiner'
        tag.artist = u'A Wilhelm Scream'
        tag.genre = u'Hardcore'
        tag.length = 150
        tag.title = u'The Soft Sell'
        tag.track = 4
        tag.year = 2005

        cache = self.mox.CreateMock(avalon.cache.IdLookupCache)
        cache.get_album_id(u'Ruiner').AndReturn(ruiner)
        cache.get_artist_id(u'A Wilhelm Scream').AndReturn(a_wilhelm_scream)
        cache.get_genre_id(u'Hardcore').AndReturn(hardcore)

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        session = self.mox.CreateMock(DummySession)
        id_gen = self.mox.CreateMockAnything(avalon.ids.get_track_id)
        model_cls = self.mox.CreateMockAnything(avalon.models.Track)
        model = self.mox.CreateMock(avalon.models.Track)

        model_cls().AndReturn(model)
        id_gen(mox.IsA(unicode)).AndReturn(uuid.UUID('450b3e88-01e0-537a-80cd-c8692c903c76'))

        session_handler.get_session().AndReturn(session)
        session.add_all([model])
        session.commit()
        session_handler.close(session)

        self.mox.ReplayAll()

        inserter = avalon.tags.insert.TrackLoader(session_handler, [tag], cache)
        inserter.insert(model_cls, id_gen)
        self.mox.VerifyAll()

    def test_insert_commit_error_session_closed(self):
        """Test that errors inserting tags do not results in leaking
        database connections.
        """
        ruiner = uuid.UUID('350c49d9-fa38-585a-a0d9-7343c8b910ed')
        a_wilhelm_scream = uuid.UUID('aa143f55-65e3-59f3-a1d8-36eac7024e86')
        hardcore = uuid.UUID('54cde78b-6d4b-5634-a666-cb7fa674c73f')

        tag = MockTag()
        tag.path = u'/home/something/music/song.flac'
        tag.album = u'Ruiner'
        tag.artist = u'A Wilhelm Scream'
        tag.genre = u'Hardcore'
        tag.length = 150
        tag.title = u'The Soft Sell'
        tag.track = 4
        tag.year = 2005

        cache = self.mox.CreateMock(avalon.cache.IdLookupCache)
        cache.get_album_id(u'Ruiner').AndReturn(ruiner)
        cache.get_artist_id(u'A Wilhelm Scream').AndReturn(a_wilhelm_scream)
        cache.get_genre_id(u'Hardcore').AndReturn(hardcore)

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        session = self.mox.CreateMock(DummySession)
        id_gen = self.mox.CreateMockAnything(avalon.ids.get_track_id)
        model_cls = self.mox.CreateMockAnything(avalon.models.Track)
        model = self.mox.CreateMock(avalon.models.Track)

        model_cls().AndReturn(model)
        id_gen(mox.IsA(unicode)).AndReturn(uuid.UUID('450b3e88-01e0-537a-80cd-c8692c903c76'))

        session_handler.get_session().AndReturn(session)
        session.add_all([model])
        session.commit().AndRaise(sqlalchemy.exc.NoSuchColumnError)
        session_handler.close(session)

        self.mox.ReplayAll()

        inserter = avalon.tags.insert.TrackLoader(session_handler, [tag], cache)
        with pytest.raises(sqlalchemy.exc.NoSuchColumnError):
            inserter.insert(model_cls, id_gen)
        self.mox.VerifyAll()




