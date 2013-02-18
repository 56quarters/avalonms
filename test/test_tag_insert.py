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

    def test_insert_without_error(self):
        pass

    def test_insert_with_error(self):
        pass


class TestTrackLoader(object):
    pass



