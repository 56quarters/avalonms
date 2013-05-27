# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2013 TSH Labs <projects@tshlabs.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""Functionality for reading audio meta data from local files using Mutagen."""

import collections
from datetime import datetime
import re

import mutagen

import avalon


__all__ = [
    'new_loader',
    'Metadata',
    'MetadataLoader',
    'MetadataDateParser',
    'MetadataTrackParser'
]


class Metadata(collections.namedtuple('_Metadata', [
    'path',
    'album',
    'artist',
    'genre',
    'title',
    'track',
    'year',
    'length'])):
    """Container for metadata of an audio file"""


def new_loader():
    """Return a new :class:`MetadataLoader` using the concrete
    Mutagen implementation, the default avalon encoding for paths,
    a default track parser, and default date parser.
    """
    track_parser = MetadataTrackParser(re.match)
    date_parser = MetadataDateParser(datetime.strptime)
    return MetadataLoader(
        mutagen,
        avalon.DEFAULT_ENCODING,
        track_parser,
        date_parser)


class MetadataLoader(object):
    """Loader for audio metadata that uses the Mutagen library and
    given parsers to convert the metadata into a somewhat normalized
    form (:class:`Metadata`).
    """

    def __init__(self, impl, path_encoding, track_parser, date_parser):
        """Set the Mutagen implementation, encoding to use for file paths,
        track number parser, and date parser.
        """
        self._impl = impl
        self._path_encoding = path_encoding
        self._track_parser = track_parser
        self._date_parser = date_parser

    def get_from_path(self, path):
        """Return audio meta data of the given file in a normalized form
         (:class:`Metadata`).

         Raise a `ValueError` if there are errors encoding the file path.
         Raise an `IOError` if the file cannot be opened or if it is an
         invalid file type. Raise a `ValueError` if the track number or
         year of the audio tag cannot be parsed.
         """
        return self._to_metadata(path, self._read_from_path(path))

    def _read_from_path(self, path):
        """Read a mutagen native for tag from the given path."""
        try:
            file_ref = self._impl.File(path.encode(self._path_encoding), easy=True)
        except UnicodeError:
            raise ValueError("Could not encode audio path [%s] to %s" % (path, self._path_encoding))
        except IOError, e:
            raise IOError("Could not open [%s]: %s" % (path, e.message))
        if file_ref is None:
            raise IOError("Invalid or unsupported audio file [%s]" % path)
        return file_ref

    def _to_metadata(self, path, file_ref):
        """Convert a Mutagen tag object into a :class:`Metadata` object."""
        audio = file_ref.info
        return Metadata(
            path=path,
            album=_get_str_val(file_ref.get('album')),
            artist=_get_str_val(file_ref.get('artist')),
            genre=_get_str_val(file_ref.get('genre')),
            length=int(audio.length),
            title=_get_str_val(file_ref.get('title')),
            track=_get_int_val(file_ref.get('tracknumber'), self._track_parser),
            year=_get_int_val(file_ref.get('date'), self._date_parser))


def _get_str_val(val):
    """Get a possibly `None` single element list as a `unicode` string"""
    if val is None:
        return unicode('')
    return unicode(val[0])


def _get_int_val(val, parser):
    """Get a possibly `None` single element list as an `int` by using
     the given parser on the element of the list
     """
    if val is None:
        return 0
    return parser.parse(val[0])


class MetadataDateParser(object):
    """Parser for extracing the year of a track.

    Some audio tags have entire timestamps for the date instead
    of just a year. Attempt to simply cast the year to an integer
    if possible. If not possible, attempt to parse it using several
    common timestamp formats (see :instance_attribute:`formats`).
    """

    formats = frozenset([
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S%z'])
    """Common timestamp formats for parsing a track year"""

    def __init__(self, parser_impl):
        """Set the date parser which is expected to behave like
        `datetime.strptime`.
        """
        self._parser = parser_impl

    def parse(self, val):
        """Attempt to parse the given date string for a year, raise a
        `ValueError` if the year could not be parsed using any known
        format.
        """
        if val.isdigit():
            return int(val)

        for fmt in self.formats:
            try:
                return self._parser(val, fmt).year
            except ValueError:
                pass
        raise ValueError("Could not parse year from value [%s]" % val)


class MetadataTrackParser(object):
    """Parser for extracting the number of a track.
    
    Some audio tags have less than perfect data for track numbers
    like "1/5", "2/5", etc. Attempt to simply cast the string to
    an integer if possible. If not possible, attempt to parse it
    as a fraction (see :instance_attribute:`fmt_fraction`).
    """

    fmt_fraction = '(\d+)/\d+'
    """Regular expression for parsing a track number"""

    def __init__(self, parser_impl):
        """Set the regular expression parser which is expected
        to behave like `re.match`.
        """
        self._parser = parser_impl

    def parse(self, val):
        """Attempt to parse the given track string, raise a `ValueError`
        if the track string could not be parsed.
        """
        if val.isdigit():
            return int(val)

        match = self._parser(self.fmt_fraction, val)
        if match is not None:
            return int(match.group(1))
        raise ValueError("Could not parse track from value [%s]" % val)

