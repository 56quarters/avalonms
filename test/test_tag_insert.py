# -*- coding: utf-8 -*-
#

import mox
import pytest

import sqlalchemy.exc

import avalon.models
import avalon.tags.insert


class DummySession(object):

    def query(self, cls):
        pass

    def commit(self):
        pass

    def close(self):
        pass

    def add_all(self, values):
        pass


class DummyQuery(object):

    def delete(self):
        pass


class MockTag(object):

    def __init__(self):
        self.path = None
        self.album = None
        self.artist = None
        self.genre = None
        self.title = None
        self.track = None
        self.year = None
        self.length = None


def id_gen_mock(val):
    return None


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

    def test_insert_invalid_attribute_error(self):
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
        tag.year = 2013

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        model_cls = self.mox.CreateMockAnything(avalon.models.Album)

        inserter = avalon.tags.insert.TrackFieldLoader(session_handler, [tag])

        with pytest.raises(AttributeError):
            inserter.insert(model_cls, id_gen_mock, 'blah')
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

        inserter = avalon.tags.insert.TrackFieldLoader(session_handler, [tag])

        with pytest.raises(AttributeError):
            inserter.insert(model_cls, id_gen_mock, 'blah')
        self.mox.VerifyAll()

    def test_insert_duplicate_ids(self):
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
        tag2.year = 2013

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        session = self.mox.CreateMock(DummySession)
        id_gen = self.mox.CreateMockAnything(id_gen_mock)
        model_cls = self.mox.CreateMockAnything(avalon.models.Album)
        model1 = self.mox.CreateMock(avalon.models.Album)
        model2 = self.mox.CreateMock(avalon.models.Album)

        model_cls().AndReturn(model1)
        id_gen(mox.IsA(unicode)).AndReturn('b6c4bfc6-c088-48af-a1c0-7bcb3f37035c')

        model_cls().AndReturn(model2)
        id_gen(mox.IsA(unicode)).AndReturn('b6c4bfc6-c088-48af-a1c0-7bcb3f37035c')

        session_handler.get_session().AndReturn(session)
        session.add_all(mox.Or(mox.In(model1), mox.In(model2)))
        session.commit()
        session_handler.close(session)

        self.mox.ReplayAll()

        inserter = avalon.tags.insert.TrackFieldLoader(
            session_handler, [tag1, tag2])

        inserter.insert(model_cls, id_gen, 'album')
        self.mox.VerifyAll()

    def test_insert_commit_error(self):
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
        tag.year = 2013

        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)
        session = self.mox.CreateMock(DummySession)
        id_gen = self.mox.CreateMockAnything(id_gen_mock)
        model_cls = self.mox.CreateMockAnything(avalon.models.Album)
        model = self.mox.CreateMock(avalon.models.Album)

        model_cls().AndReturn(model)
        id_gen(mox.IsA(unicode)).AndReturn('b6c4bfc6-c088-48af-a1c0-7bcb3f37035c')

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
        id_gen = self.mox.CreateMockAnything(id_gen_mock)
        model_cls = self.mox.CreateMockAnything(avalon.models.Album)
        model = self.mox.CreateMock(avalon.models.Album)

        model_cls().AndReturn(model)
        id_gen(mox.IsA(unicode)).AndReturn('b6c4bfc6-c088-48af-a1c0-7bcb3f37035c')

        session_handler.get_session().AndReturn(session)
        session.add_all([model])
        session.commit()
        session_handler.close(session)

        self.mox.ReplayAll()

        inserter = avalon.tags.insert.TrackFieldLoader(session_handler, [tag])
        inserter.insert(model_cls, id_gen, 'album')
        self.mox.VerifyAll()


class TestTrackLoader(object):
    pass



