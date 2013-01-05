# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright (c) 2012 TSH Labs <projects@tshlabs.org>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


"""Functionality for reading audio metadata from local files using
either the TagPy or Mutagen libraries.
"""


import collections
import re
from datetime import datetime

try:
    import mutagen
except ImportError:
    _have_mutagen = False
else:
    _have_mutagen = True

try:
    import tagpy
except ImportError:
    _have_tagpy = False
else:
    _have_tagpy = True

import avalon


__all__ = [
    'Metadata',
    'MetadataLoader',
    'MetadataDateParser',
    'MetadataTrackParser',
    'new_loader',
    'read_tagpy',
    'read_mutagen',
    'from_tagpy',
    'from_mutagen'
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

    """Container for metadata of audio file"""


class MetadataLoader(object):

    """Use a given reader and factory method to load
    audio metadata based on the file path.
    """

    def __init__(self, reader, factory):
        """Set the reader and factory callables to use (TagPy
        or Mutagen based).
        """
        self._reader = reader
        self._factory = factory

    def get_from_path(self, path):
        """Get a Metadata object representing the audio file at
        the given path. Raise an IOError if there is an error
        reading the file or it is not a valid type. Raise a 
        ValueError if the tag contains invalid data.
        """
        return self._factory(path, self._reader(path))


def new_loader():
    """Construct a new metadata loader based on which audio 
    tag libraries are available. Raise a NotImplementedError
    if neither TagPy or Mutagen is installed.
    """
    if _have_mutagen:
        return MetadataLoader(read_mutagen, from_mutagen)
    elif _have_tagpy:
        return MetadataLoader(read_tagpy, from_tagpy)
    raise NotImplementedError("Did not find supported tag library")


def read_tagpy(path, impl=None):
    """Get a TagPy native tag representation"""
    if impl is None:
        impl = tagpy
    try:
        file_ref = impl.FileRef(path.encode(avalon.DEFAULT_ENCODING))
    except UnicodeError, e:
        raise IOError("Could not encode audio path [%s]" % e.message)
    except ValueError:
        raise IOError("Invalid or unsupported audio file [%s]" % path)
    if file_ref.tag() is None:
        raise IOError("Invalid or unsupported audio file [%s]" % path)
    return file_ref


def read_mutagen(path, impl=None):
    """Get a Mutagen native tag representation"""
    if impl is None:
        impl = mutagen
    try:
        file_ref = impl.File(path.encode(avalon.DEFAULT_ENCODING), easy=True)
    except IOError, e:
        raise IOError("Could not open [%s]: %s" % (path, e.message))
    if file_ref is None:
        raise IOError("Invalid or unsupported audio file [%s]" % path)
    return file_ref


class MetadataDateParser(object):
    
    """Parser for extracing the year of a track

    Some audio tags have entire timestamps for the date instead
    of just a year.
    """

    fmt_iso = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, parser_impl):
        """Set the date parser which is expected to behave like
        datetime.strptime().
        """
        self._parser = parser_impl

    def parse(self, val):
        """Attempt to parse the given date string for a year, raise a
        ValueError if the year could not be parsed.
        """
        if val.isdigit():
            return int(val)

        try:
            ts = self._parser(val, self.fmt_iso)
        except ValueError:
            raise ValueError("Could not parse year from value [%s]" % val)
        return ts.year


class MetadataTrackParser(object):
    
    """Parser for extracting the number of a track.
    
    Some audio tags have less than perfect data for track numbers
    like "1/5", "2/5", etc.
    """

    fmt_fraction = '(\d+)/\d+'

    def __init__(self, parser_impl):
        """Set the regular expression parser which is expected
        to behave like re.match().
        """
        self._parser = parser_impl

    def parse(self, val):
        """Attempt to parse the given track string, raise the ValueError
        if the track string could not be parsed.
        """
        if val.isdigit():
            return int(val)

        match = self._parser(self.fmt_fraction, val)
        if match is not None:
            return int(match.group(1))
        raise ValueError("Could not parse track from value [%s]" % val)


# Default parser to use for converting various formats
# of track number into a plain integer.
_track_parser = MetadataTrackParser(re.match)


# Default parser to use for converting various types of
# date like values into a plain old year.
_date_parser = MetadataDateParser(datetime.strptime)


def _norm_list_str(val):
    """Convert a possibly-None single element list into a unicode
    string.
    """
    if val is None:
        return unicode('')
    return unicode(val[0])


def _norm_list_track(val):
    """Convert a possibly-None single element list into a track 
    number (integer).
    """
    if val is None:
        return 0
    return _track_parser.parse(val[0])


def _norm_list_date(val):
    """Convert a possibly-None single element list into a year 
    (integer).
    """
    if val is None:
        return 0
    return _date_parser.parse(val[0])


def from_tagpy(path, meta):
    """Convert a TagPy tag object into a Metadata object"""
    # TagPy wraps Taglib which does all the data coercion
    # for us so we don't have to do any parsing on our own
    tag = meta.tag()
    audio = meta.audioProperties()
    return Metadata(
        path=path,
        album=tag.album,
        artist=tag.artist,
        genre=tag.genre,
        length=int(audio.length),
        title=tag.title,
        track=int(tag.track),
        year=int(tag.year))


def from_mutagen(path, meta):
    """Convert a Mutagen tag object into a Metadata object"""
    audio = meta.info
    return Metadata(
        path=path,
        album=_norm_list_str(meta.get('album')),
        artist=_norm_list_str(meta.get('artist')),
        genre=_norm_list_str(meta.get('genre')),
        length=int(audio.length),
        title=_norm_list_str(meta.get('title')),
        track=_norm_list_track(meta.get('tracknumber')),
        year=_norm_list_date(meta.get('date')))

