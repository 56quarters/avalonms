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


"""Functionality for crawling a filesystem to find valid audio files."""


import os
import os.path


__all__ = [
    'get_files',
    'get_tags',
    'is_valid_file'
    'VALID_EXTS'
    ]


VALID_EXTS = frozenset(['.mp3', '.ogg', '.flac'])


def _get_files(callback, root):
    """Get a list of files under the given root filtered
    using the supplied callback.
    """
    out = []
    for root, dirs, files in os.walk(root):
        for entry in files:
            out.append(os.path.normpath(os.path.join(root, entry)))
    return [entry for entry in out if callback(entry)]


def get_files(root):
    """Get a list of supported files (indicated by VALID_EXTS)
    under the given root.
    """
    # Force a unicode object here so that we get unicode
    # objects back for paths so that we can treat path the
    # same as we treat tag values.
    return _get_files(is_valid_file, unicode(root))


def is_valid_file(path):
    """Return true if the path is a audio file that is
    supported (by extension), false otherwise.
    """
    return os.path.splitext(path)[1] in VALID_EXTS


def get_tags(files, loader):
    """Get a list of Metadata objects for each audio file."""
    return [loader.get_from_path(path) for path in files]

