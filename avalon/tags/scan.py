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

