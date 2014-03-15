# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


"""Functionality for crawling a filesystem to find audio files."""

import os


__all__ = [
    'get_files',
    'TagCrawler'
]


def get_files(root):
    """Get a list of files under the given root.
    """
    out = []
    # Force a unicode object here so that we get unicode
    # objects back for paths so that we can treat path the
    # same as we treat tag values.
    for root, dirs, files in os.walk(unicode(root)):
        for entry in files:
            out.append(os.path.normpath(os.path.join(root, entry)))
    return out


class TagCrawler(object):
    """Use the given metadata loader to read information for
    each audio file.
    """

    def __init__(self, loader, log):
        """Set the tag metadata loader and logger."""
        self._loader = loader
        self._log = log

    def get_tags(self, files):
        """Get a list of Metadata objects for each audio file,
        logging a warning if there was an issue reading the file
        or parsing the tag info.
        """
        out = []
        for tag_file in files:
            try:
                out.append(self._loader.get_from_path(tag_file))
            except IOError, e:
                self._log.warn(e.message)
            except ValueError, e:
                self._log.warn(e.message)
        return out

