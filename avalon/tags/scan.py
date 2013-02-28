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

