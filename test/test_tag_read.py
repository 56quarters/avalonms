# -*- coding: utf-8 -*-
#

import re
from datetime import datetime

import mox
import pytest

import avalon.tags.read


class MutagenMock(object):
    def File(self, path, easy=False):
        pass


class MutagenFileMock(object):
    def __init__(self):
        self.info = None
    def get(self, key):
        pass


class MutagenAudioMock(object):
    def __init__(self):
        self.length = None


class TestMetadataDateParser(object):

    def test_is_digit(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
        assert 2001 == parser.parse(u'2001')

    def test_is_timestamp_1(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
        assert 2001 == parser.parse(u'2001-01-01 14:01:59')

    def test_is_timestamp_2(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
        assert 2003 == parser.parse(u'2003-01-01T14:01:59')

    def test_is_timestamp_3(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
        assert 2001 == parser.parse(u'2001-01-01T14:01:59+0400')

    def test_is_invalid(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)

        with pytest.raises(ValueError):
            parser.parse('Something')


class TestMetadataTrackParser(object):

    def test_is_digit(self):
        parser = avalon.tags.read.MetadataTrackParser(re.match)
        assert 1 == parser.parse(u'1')

    def test_is_fraction(self):
        parser = avalon.tags.read.MetadataTrackParser(re.match)
        assert 2 == parser.parse(u'2/5')

    def test_is_invalid(self):
        parser = avalon.tags.read.MetadataTrackParser(re.match)

        with pytest.raises(ValueError):
            parser.parse(u'Blah')

