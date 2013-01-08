# -*- coding: utf-8 -*-
#

import mox
import pytest

import avalon.models
import avalon.tags.insert

class TestCleaner(object):

    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_clean_without_error(self):
        session_handler = self.mox.CreateMock(avalon.models.SessionHandler)

    def test_clean_with_error(self):
        pass


class TestTrackFieldLoader(object):

    def test_insert_without_error(self):
        pass

    def test_insert_with_error(self):
        pass


class TestTrackLoader(object):
    pass



