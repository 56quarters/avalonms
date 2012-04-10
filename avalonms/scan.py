# -*- coding: utf-8 -*-
#


"""
"""


import os
import os.path

import tagpy

from avalonms.models import TrackModel


__all__ = [
    'get_files',
    'get_tags',
    'is_valid_file'
    'ScannedTrack',
    'VALID_EXTS'
    ]


VALID_EXTS = set(['.mp3', '.mp2', '.ogg', '.flac'])


def is_valid_file(path):
    """
    """
    return os.path.splitext(path)[1] in VALID_EXTS


def get_files(root):
    """
    """
    out = []
    for root, dirs, files in os.walk(root):
        for entry in files:
            path = os.path.join(root, entry)
            if not is_valid_file(path):
                continue
            out.append(path)
    return out
    

def get_tags(files):
    """
    """
    out = {}
    for path in files:
        ref = tagpy.FileRef(path)
        tag = ref.tag()
        out[path] = ScannedTrack.from_tag(tag)
    return out


class ScannedTrack(object):

    """
    """

    def __init__(self):
        """
        """
        self.album = None
        self.artist = None
        self.genre = None
        self.title = None
        self.track = None
        self.year = None

    def __repr__(self):
        """
        """
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
        out = cls()
        out.album = tag.album
        out.artist = tag.artist
        out.genre = tag.genre
        out.title = tag.title
        out.track = tag.track
        out.year = tag.year
        return out


