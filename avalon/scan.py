# -*- coding: utf-8 -*-
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


""" Functions for scanning a music collection for metadata."""


import os
import os.path

import tagpy


__all__ = [
    'get_files',
    'get_tags',
    'is_valid_file'
    'ScannedTrack',
    'VALID_EXTS'
    ]


VALID_EXTS = frozenset(['.mp3', '.mp2', '.ogg', '.flac'])


def is_valid_file(path):
    """ Return true if the path is a audio file that is
        supported (by extension), false otherwise.
    """
    return os.path.splitext(path)[1] in VALID_EXTS


def get_files(root):
    """ Get a list of supported files under the given root.
    """
    out = []
    for root, dirs, files in os.walk(root):
        for entry in files:
            path = os.path.normpath(os.path.join(root, entry))
            if not is_valid_file(path):
                continue
            out.append(path)
    return out
    

def get_tags(files):
    """ Get a dictionary of metadata ScannedTrack objects for
        each audio file indexed by its path.
    """
    out = {}
    for path in files:
        ref = tagpy.FileRef(path)
        tag = ref.tag()
        out[path] = ScannedTrack.from_tag(tag)
    return out


class ScannedTrack(object):

    """ Container for metadata of an audio file.
    """

    def __init__(self):
        """ Initialize each metadata field to None.
        """
        self.album = None
        self.artist = None
        self.genre = None
        self.title = None
        self.track = None
        self.year = None

    def __repr__(self):
        return (
            '<%s: '
            'album=%s, '
            'artist=%s, '
            'genre=%s '
            'title=%s, '
            'track=%s, '
            'year=%s>') % (
            self.__class__.__name__,
            self.album,
            self.artist,
            self.genre,
            self.title,
            self.track,
            self.year)

    @classmethod
    def from_tag(cls, tag):
        """ Create a new instance from a TagPy tag object.
        """
        out = cls()
        out.album = tag.album
        out.artist = tag.artist
        out.genre = tag.genre
        out.title = tag.title
        out.track = tag.track
        out.year = tag.year
        return out


