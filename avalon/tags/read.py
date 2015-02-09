# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Functionality for reading audio metadata from local files using Mutagen."""

from __future__ import absolute_import, unicode_literals
import collections

import avalon.compat


Metadata = collections.namedtuple('Metadata', [
    'path',
    'album',
    'artist',
    'genre',
    'title',
    'track',
    'year',
    'length'])


class MetadataLoader(object):
    """Loader for audio metadata that uses the Mutagen library and
    given parsers to convert the metadata into a somewhat normalized
    form (:class:`Metadata`).
    """

    def __init__(self, impl, track_parser, date_parser):
        """Set the Mutagen implementation, encoding to use for file paths,
        track number parser, and date parser.

        :param impl: Mutagen module implementation (easier testing)
        :param MetadataTrackParser track_parser: Parser for audio file track
            numbers
        :param MetadataDateParser date_parser: Parser for audio file recording
            years
        """
        self._impl = impl
        self._track_parser = track_parser
        self._date_parser = date_parser

    def get_from_path(self, path):
        """Return audio metadata of the given file in a normalized form
         (:class:`Metadata`).

         :param unicode path: Path to a media file to read metadata from
         :returns: Metadata for the given file it is a supported type
         :rtype: Metadata
         :raises ValueError: If there are errors encoding the file path,
            the track number of the audio tag cannot be parsed, or the
            year of the audio tag cannot be parsed.
         :raises IOError: If the file cannot be opened or if it is an
            invalid file type.
         """
        return self._to_metadata(path, self._read_from_path(path))

    def _read_from_path(self, path):
        """Read a mutagen native tag from the given path."""
        try:
            file_ref = self._impl.File(path, easy=True)
        except IOError as e:
            raise IOError("Could not open {0}: {1}".format(path, e))
        if file_ref is None:
            raise IOError("Invalid or unsupported audio file {0}".format(path))
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
    """Get a possibly `None` single element list as a `unicode` string."""
    if val is None:
        return avalon.compat.to_text(None)
    return avalon.compat.to_text(val[0])


def _get_int_val(val, parser):
    """Get a possibly `None` single element list as an `int` by using
     the given parser on the element of the list.
     """
    if val is None:
        return 0
    return parser.parse(val[0])


class MetadataDateParser(object):
    """Parser for extracting the year of a track.

    Some audio tags have entire timestamps for the date instead
    of just a year. Attempt to simply cast the year to an integer
    if possible. If not possible, attempt to parse it using several
    common timestamp formats (see :instance_attribute:`formats`).

    :cvar frozenset formats: Common timestamp formats for parsing a
        track year.
    """

    formats = frozenset([
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S'])

    def __init__(self, parser_impl):
        """Set the date parser which is expected to behave like
        :func:`datetime.strptime`.

        :param function parser_impl: Datetime parser
        """
        self._parser = parser_impl

    def parse(self, val):
        """Attempt to parse the given date string for a year, raise a
        :class:`ValueError` if the year could not be parsed using any
        known format.

        :param str val: Track year metadata to parse a year out of
        :return: The parsed year of the audio file metadata
        :rtype: int
        :raises ValueError: If the year could not be parsed from the
            given date string
        """
        if val.isdigit():
            return int(val)

        for fmt in self.formats:
            try:
                return self._parser(val, fmt).year
            except ValueError:
                pass
        raise ValueError("Could not parse year from value {0}".format(val))


class MetadataTrackParser(object):
    """Parser for extracting the number of a track.

    Some audio tags have less than perfect data for track numbers
    like "1/5", "2/5", etc. Attempt to simply cast the string to
    an integer if possible. If not possible, attempt to parse it
    as a fraction (see :instance_attribute:`fmt_fraction`).

    :cvar str fmt_fraction: Regular expression for parsing a track
        number
    """

    fmt_fraction = r'(\d+)/\d+'

    def __init__(self, parser_impl):
        """Set the regular expression parser which is expected
        to behave like :func:`re.match`.

        :param function parser_impl: Regular expression matcher
        """
        self._parser = parser_impl

    def parse(self, val):
        """Attempt to parse the given track string, raise a
        :class:`ValueError` if the track string could not be parsed.

        :param str val: Track number metadata string to parse a track
            number out of
        :return: The parsed track number of the audio file metadata
        :rtype: int
        :raises ValueError: If the track number could not be parsed from
            the given track number string.
        """
        if val.isdigit():
            return int(val)

        match = self._parser(self.fmt_fraction, val)
        if match is not None:
            return int(match.group(1))
        raise ValueError("Could not parse track from value {0}".format(val))
