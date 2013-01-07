# -*- coding: utf-8 -*-
#

import unittest


class TestReadTagpy(unittest.TestCase):

    def test_unicode_error(self):
        pass

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

