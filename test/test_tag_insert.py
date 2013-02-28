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

    def test_clean_without_error(self):
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
        pass

    def test_insert_commit_error(self):
        pass


class TestTrackLoader(object):
    pass



