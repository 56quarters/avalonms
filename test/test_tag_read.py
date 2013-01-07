# -*- coding: utf-8 -*-
#

import unittest

import mox
import pytest

import avalon.tags.read


class TagpyMock(object):
    def FileRef(self, path):
        pass


class MutagenMock(object):
    def File(self, path, easy=True):
        pass


class TestReadTagpy(unittest.TestCase):

    def setup_method(self, method):
        self.mox = mox.Mox()
        self.tagpy = self.mox.CreateMock(TagpyMock)

    def test_unicode_error(self):
        self.tagpy.FileRef(mox.IsA(unicode)).AndRaise(UnicodeDecodeError("Could not do something"))
        self.mox.ReplayAll()

        with pytest.raises(IOError):
            avalon.tags.read.read_tagpy(unicode('/path/file'), self.tagpy)

        self.mox.VerifyAll()

    def test_value_error(self):
        pass

    def test_invalid_tag(self):
        pass

    def test_success(self):
        pass


class TestReadMutagen(unittest.TestCase):

    def test_unicode_error(self):
        pass

    def test_ioerror(self):
        pass

    def test_invalid_tag(self):
        pass

    def test_success(self):
        pass


class TestMetadataDateParser(unittest.TestCase):

    def test_is_digit(self):
        pass

    def test_is_timestamp(self):
        pass

    def test_is_invalid(self):
        pass


class TestMetadataTrackParser(unittest.TestCase):

    def test_is_digit(self):
        pass

    def test_is_fraction(self):
        pass

    def test_is_invalid(self):
        pass


class TestFromTagpy(unittest.TestCase):

    def test_invalid_track(self):
        pass

    def test_invalid_year(self):
        pass

    def test_success(self):
        pass


class TestFromMutagen(unittest.TestCase):

    def test_invalid_track(self):
        pass

    def test_invalid_year(self):
        pass

    def test_none_album(self):
        pass

    def test_success(self):
        pass

