# -*- coding: utf-8 -*-
#

from __future__ import absolute_import, unicode_literals
import mock

import avalon.log
import avalon.tags.read
import avalon.tags.crawl


class DummyWalk(object):
    """Dummy implementation of os.walk that allows us to return \
    some exact list of files
    """

    def __init__(self, files):
        self._files = files

    def __call__(self, root, *args, **kwargs):
        yield root, '', self._files


class TestTagCrawler(object):
    def test_get_tags_io_error(self):
        """Test that exceptions when loading tags are dealt with quietly"""
        loader = mock.Mock(spec=avalon.tags.read.MetadataLoader)
        files = ['path.ogg', 'path2.ogg']

        loader.get_from_path.side_effect = [IOError("OH NOES"), IOError("OH NOES")]
        crawler = avalon.tags.crawl.TagCrawler(loader, 'music', DummyWalk(files))
        out = crawler.get_tags()

        assert 0 == len(out)

    def test_get_tags_io_error_unicode_error_message(self):
        """Test that exceptions when loading tags are dealt with quietly and \
        unicode characters in error messages don't cause encoding issues.
        """
        loader = mock.Mock(spec=avalon.tags.read.MetadataLoader)
        files = ['path.ogg', 'path2.ogg']

        loader.get_from_path.side_effect = [IOError('OH NOES! Verás'), IOError('OH NOES! Verás')]
        crawler = avalon.tags.crawl.TagCrawler(loader, 'music', DummyWalk(files))
        out = crawler.get_tags()

        assert 0 == len(out)

    def test_get_tags_value_error(self):
        """ Test that exceptions when parsing tags are dealt with quietly"""
        loader = mock.Mock(spec=avalon.tags.read.MetadataLoader)
        files = ['path.ogg', 'path2.ogg']

        loader.get_from_path.side_effect = [ValueError("OH NOES"), ValueError("OH NOES")]
        crawler = avalon.tags.crawl.TagCrawler(loader, 'music', DummyWalk(files))
        out = crawler.get_tags()

        assert 0 == len(out)

    def test_get_tags_value_error_unicode_error_message(self):
        """ Test that exceptions when parsing tags are dealt with quietly and \
        unicode characters in error messages don't cause encoding issues.
        """
        loader = mock.Mock(spec=avalon.tags.read.MetadataLoader)
        files = ['path.ogg', 'path2.ogg']

        loader.get_from_path.side_effect = [
            ValueError("OH NOES! There's a problem in Düsseldorf!"),
            ValueError("OH NOES! There's a problem in Düsseldorf!")]
        crawler = avalon.tags.crawl.TagCrawler(loader, 'music', DummyWalk(files))
        out = crawler.get_tags()

        assert 0 == len(out)

    def test_get_tags_success(self):
        """Test tags can be crawled when tags are able to be loaded correctly"""
        loader = mock.Mock(spec=avalon.tags.read.MetadataLoader)
        files = ['path.ogg', 'path2.ogg']

        loader.get_from_path.side_effect = [None, None]

        crawler = avalon.tags.crawl.TagCrawler(loader, 'music', DummyWalk(files))
        out = crawler.get_tags()

        assert 2 == len(out)

