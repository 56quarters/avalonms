# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals
from datetime import datetime

import pytest
import re
import mock
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
        assert 2001 == parser.parse('2001')

    def test_is_timestamp_1(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
        assert 2001 == parser.parse('2001-01-01 14:01:59')

    def test_is_timestamp_2(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
        assert 2003 == parser.parse('2003-01-01T14:01:59')

    def test_is_invalid(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
        with pytest.raises(ValueError):
            parser.parse('Something')


class TestMetadataTrackParser(object):
    def test_is_digit(self):
        parser = avalon.tags.read.MetadataTrackParser(re.match)
        assert 1 == parser.parse('1')

    def test_is_fraction(self):
        parser = avalon.tags.read.MetadataTrackParser(re.match)
        assert 2 == parser.parse('2/5')

    def test_is_invalid(self):
        parser = avalon.tags.read.MetadataTrackParser(re.match)
        with pytest.raises(ValueError):
            parser.parse('Blah')


class TestMetadataLoader(object):
    def test_get_from_path_unicode_error(self):
        impl = mock.Mock(spec=MutagenMock)
        track_parser = mock.Mock(spec=avalon.tags.read.MetadataTrackParser)
        date_parser = mock.Mock(spec=avalon.tags.read.MetadataDateParser)

        impl.File.side_effect = UnicodeError("Bah!")

        loader = avalon.tags.read.MetadataLoader(impl, track_parser, date_parser)

        with pytest.raises(ValueError):
            loader.get_from_path('/blah/some.ogg')

    def test_get_from_path_io_error(self):
        impl = mock.Mock(spec=MutagenMock)
        track_parser = mock.Mock(spec=avalon.tags.read.MetadataTrackParser)
        date_parser = mock.Mock(spec=avalon.tags.read.MetadataDateParser)

        impl.File.side_effect = IOError("Bah!")
        loader = avalon.tags.read.MetadataLoader(impl, track_parser, date_parser)

        with pytest.raises(IOError):
            loader.get_from_path('/blah/thing.ogg')

    def test_get_from_path_none_return(self):
        impl = mock.Mock(spec=MutagenMock)
        track_parser = mock.Mock(spec=avalon.tags.read.MetadataTrackParser)
        date_parser = mock.Mock(spec=avalon.tags.read.MetadataDateParser)

        impl.File.return_value = None
        loader = avalon.tags.read.MetadataLoader(impl, track_parser, date_parser)

        with pytest.raises(IOError):
            loader.get_from_path('/blah/bad.ogg')

    def test_get_from_path_to_metadata_parse_error(self):
        impl = mock.Mock(spec=MutagenMock)
        tag = mock.Mock(spec=MutagenFileMock)
        track_parser = mock.Mock(spec=avalon.tags.read.MetadataTrackParser)
        date_parser = mock.Mock(spec=avalon.tags.read.MetadataDateParser)

        impl.File.return_value = tag
        tag.info = mock.Mock(spec=MutagenAudioMock)
        tag.info.length = 123
        tag.get.return_value = ['']

        track_parser.parse.side_effect = ValueError("Bah!")
        loader = avalon.tags.read.MetadataLoader(impl, track_parser, date_parser)

        with pytest.raises(ValueError):
            loader.get_from_path('/blah/blah.ogg')
