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


class TestMetadataLoader(object):
    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_get_from_path_unicodeerror(self):
        encoding = 'utf-8'
        impl = self.mox.CreateMock(MutagenMock)
        track_parser = self.mox.CreateMock(avalon.tags.read.MetadataTrackParser)
        date_parser = self.mox.CreateMock(avalon.tags.read.MetadataDateParser)

        impl.File(mox.IsA(basestring), easy=True).AndRaise(UnicodeError)
        self.mox.ReplayAll()

        loader = avalon.tags.read.MetadataLoader(impl, encoding, track_parser, date_parser)

        with pytest.raises(ValueError):
            loader.get_from_path(u'/blah/some.ogg')

    def test_get_from_path_ioerror(self):
        encoding = 'utf-8'
        impl = self.mox.CreateMock(MutagenMock)
        track_parser = self.mox.CreateMock(avalon.tags.read.MetadataTrackParser)
        date_parser = self.mox.CreateMock(avalon.tags.read.MetadataDateParser)

        impl.File(mox.IsA(basestring), easy=True).AndRaise(IOError)
        self.mox.ReplayAll()

        loader = avalon.tags.read.MetadataLoader(impl, encoding, track_parser, date_parser)

        with pytest.raises(IOError):
            loader.get_from_path(u'/blah/thing.ogg')

    def test_get_from_path_none_return(self):
        encoding = 'utf-8'
        impl = self.mox.CreateMock(MutagenMock)
        track_parser = self.mox.CreateMock(avalon.tags.read.MetadataTrackParser)
        date_parser = self.mox.CreateMock(avalon.tags.read.MetadataDateParser)

        impl.File(mox.IsA(basestring), easy=True).AndReturn(None)
        self.mox.ReplayAll()

        loader = avalon.tags.read.MetadataLoader(impl, encoding, track_parser, date_parser)

        with pytest.raises(IOError):
            loader.get_from_path(u'/blah/bad.ogg')

    def test_get_from_path_to_metadata_parse_error(self):
        encoding = 'utf-8'
        impl = self.mox.CreateMock(MutagenMock)
        tag = self.mox.CreateMock(MutagenFileMock)
        track_parser = self.mox.CreateMock(avalon.tags.read.MetadataTrackParser)
        date_parser = self.mox.CreateMock(avalon.tags.read.MetadataDateParser)

        impl.File(mox.IsA(basestring), easy=True).AndReturn(tag)
        tag.info = MutagenAudioMock()
        tag.info.length = 123
        tag.get('album').AndReturn([u''])
        tag.get('artist').AndReturn([u''])
        tag.get('genre').AndReturn([u''])
        tag.get('title').AndReturn([u''])
        tag.get('tracknumber').AndReturn([u''])
        tag.get('date').AndReturn([u''])

        track_parser.parse(mox.IsA(basestring)).AndRaise(ValueError)
        self.mox.ReplayAll()

        loader = avalon.tags.read.MetadataLoader(impl, encoding, track_parser, date_parser)

        with pytest.raises(ValueError):
            loader.get_from_path(u'/blah/blah.ogg')
