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
    import tagpy
except ImportError:
    have_tagpy = False
else:
    have_tagpy = True

try:
    import mutagen
except ImportError:
    have_mutagen = False
else:
    have_mutagen = True

if not have_tagpy and not have_mutagen:
    raise ImportError("TagPy or Mutagen could not be imported")

import avalon.exc


__all__ = [
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

    def get_from_path(self, path):
        meta = None

        try:
            meta = self._reader(path)
        except IOError, e:
            pass

        try:
            return self._factory(meta)
        except ValueError, e:
            pass


def read_tagpy(path):
    """ """
    file_ref = None
    try:
        file_ref = tagpy.FileRef(path.encode(avalon.DEFAULT_ENCODING))
    except UnicodeError, e:
        raise IOError("Could not encode audio path: %s" % str(e))
    except ValueError, e:
        raise IOError("Could not open [%s]: %s" % (path, str(e)))
    return file_ref.tag()


def read_mutagen(path):
    """ """
    tag_file = None
    try:
        tag_file = mutagen.File(path, easy=True)
    except IOError, e:
        raise IOError("Could not open [%s]: %s" % (path, str(e)))
    if tag_file is None:
        raise IOError("Invalid audio file [%s]" % path)
    return tag_file


def from_tagpy(path, meta):
    """ """
    return Metadata(
        path=path,
        album=meta.album,
        artist=meta.artist,
        genre=meta.genre,
        title=meta.title,
        track=int(meta.track),
        year=int(meta.year))


def from_mutagen(path, meta):
    """ """
    return Metadata(
        path=path,
        album=meta.get('album')[0],
        artist=meta.get('artist')[0],
        genre=meta.get('genre')[0],
        title=meta.get('title')[0],
        track=int(meta.get('tracknumber')[0]),
        year=int(meta.get('date')[0]))

