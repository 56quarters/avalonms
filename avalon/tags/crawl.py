# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Functionality for crawling a filesystem to find audio files."""

from __future__ import absolute_import, unicode_literals
import os

import avalon.log
import avalon.compat


class TagCrawler(object):
    """Use the given metadata loader to read information for
    each audio file under the given music collection root.
    """

    _logger = avalon.log.get_error_log()

    def __init__(self, loader, root, walk_impl=None):
        """Set the metadata loader, music collection root and optionally
        the :func:`os.walk` implementation to use (to allow for easier unit
        testing).

        :param avalon.tags.read.MetadataLoader loader: Metadata loader for
            reading discovered audio files from disk
        :param str root: Base path to the music collection to crawl recursively
        :param function walk_impl: Implementation of a function to recursively
            crawl a file system (expected to behave like :func:`os.walk`).
        """
        if walk_impl is None:
            walk_impl = os.walk

        self._loader = loader
        self._root = root
        self._walk = walk_impl

    def _get_files(self):
        out = []
        # Force a unicode object here so that we get unicode
        # objects back for paths so that we can treat path the
        # same as we treat tag values. It will usually be the case
        # that the path has already been converted to a unicode
        # object but it doesn't hurt to make sure.
        for root, _, files in self._walk(avalon.compat.to_text(self._root)):
            for entry in files:
                out.append(os.path.normpath(os.path.join(root, entry)))
        return out

    def get_tags(self):
        """Get a list of Metadata objects for each audio file,
        logging a warning if there was an issue reading the file
        or parsing the tag info.

        :return: List of all audio file metadata under the music collection
            root path that could be read
        :rtype: list
        """
        files = self._get_files()
        self._logger.info(
            "Attempting to load metadata for %s files...", len(files))

        # Note that we're passing args[0] of each exception to the
        # calls to the logger. This is because the logger expects a
        # unicode object as a message and accessing args[0] directly
        # is the only way to reliably get the message as a text type
        # in both Python 2 and Python 3 (that I've found in my testing).
        out = []
        for tag_file in files:
            try:
                out.append(self._loader.get_from_path(tag_file))
            except ValueError as e:
                self._logger.warn(avalon.compat.to_text(e.args[0]))
            except IOError as e:
                # IOError usually just means we tried to read an audio
                # tag from a file that isn't an actual audio file (like
                # a .jpg) or a file that doesn't have metadata (.wav).
                # Just let it pass at INFO.
                self._logger.info(avalon.compat.to_text(e.args[0]))
        return out

