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


import collections

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


import avalon.exc


__all__ = [
    'Metadata',
    'MetadataLoader',
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
            'year'])):

    """Container for metadata of audio file"""


class MetadataLoader(object):

    def __init__(self, reader, factory):
        self._reader = reader
        self._factory = factory

    @classmethod
    def factory(cls):
        if _have_mutagen:
            return cls(read_mutagen, from_mutagen)
        elif _have_tagpy:
            return cls(read_tagpy, from_tagpy)
        raise NotImplementedError("Did not find supported tag library")

    def get_from_path(self, path):
        return self._factory(path, self._reader(path))


def read_tagpy(path):
    """Get a TagPy tag metadata representation"""
    file_ref = None
    try:
        file_ref = tagpy.FileRef(path.encode(avalon.DEFAULT_ENCODING))
    except UnicodeError, e:
        raise IOError("Could not encode audio path: %s" % str(e))
    except ValueError, e:
        raise IOError("Could not open [%s]: %s" % (path, str(e)))
    return file_ref.tag()


def read_mutagen(path):
    """Get a Mutagen tag metadata representation"""
    tag_file = None
    try:
        tag_file = mutagen.File(path, easy=True)
    except IOError, e:
        raise IOError("Could not open [%s]: %s" % (path, str(e)))
    if tag_file is None:
        raise IOError("Invalid audio file [%s]" % path)
    return tag_file


def _norm_list_str(val):
    """Convert a possibly-None single element list into a unicode string"""
    if val is None:
        return unicode('')
    return unicode(val[0])


def _norm_list_int(val):
    """Convert a possibly-None single elemtn list into an integer"""
    if val is None:
        return 0
    return int(val[0])


def from_tagpy(path, meta):
    """Convert a TagPy tag object into a Metadata object"""
    return Metadata(
        path=path,
        album=meta.album,
        artist=meta.artist,
        genre=meta.genre,
        title=meta.title,
        track=int(meta.track),
        year=int(meta.year))


def from_mutagen(path, meta):
    """Convert a Mutagen tag object into a Metadata object"""
    return Metadata(
        path=path,
        album=_norm_list_str(meta.get('album')),
        artist=_norm_list_str(meta.get('artist')),
        genre=_norm_list_str(meta.get('genre')),
        title=_norm_list_str(meta.get('title')),
        track=_norm_list_int(meta.get('tracknumber')),
        year=_norm_list_int(meta.get('date')))

