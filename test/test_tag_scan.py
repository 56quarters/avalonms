# -*- coding: utf-8 -*-
#

import mox

import avalon.log
import avalon.tags.read
import avalon.tags.scan


class TestTagCrawler(object):

    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_get_tags_io_error(self):
        loader = self.mox.CreateMock(avalon.tags.read.MetadataLoader)
        logger = self.mox.CreateMock(avalon.log.AvalonLog)
        files = ['path.ogg', 'path2.ogg']

        loader.get_from_path(files[0]).AndRaise(IOError("OH NOES"))
        logger.warn(mox.IsA(basestring))
        loader.get_from_path(files[1]).AndRaise(IOError("OH NOES"))
        logger.warn(mox.IsA(basestring))

        self.mox.ReplayAll()

        crawler = avalon.tags.scan.TagCrawler(loader, logger)
        out = crawler.get_tags(files)

        assert 0 == len(out)
        self.mox.VerifyAll()

    def test_get_tags_value_error(self):
        loader = self.mox.CreateMock(avalon.tags.read.MetadataLoader)
        logger = self.mox.CreateMock(avalon.log.AvalonLog)
        files = ['path.ogg', 'path2.ogg']

        loader.get_from_path(files[0]).AndRaise(ValueError("OH NOES"))
        logger.warn(mox.IsA(basestring))
        loader.get_from_path(files[1]).AndRaise(ValueError("OH NOES"))
        logger.warn(mox.IsA(basestring))

        self.mox.ReplayAll()

        crawler = avalon.tags.scan.TagCrawler(loader, logger)
        out = crawler.get_tags(files)

        assert 0 == len(out)
        self.mox.VerifyAll()

    def test_get_tags_success(self):
        loader = self.mox.CreateMock(avalon.tags.read.MetadataLoader)
        logger = self.mox.CreateMock(avalon.log.AvalonLog)
        files = ['path.ogg', 'path2.ogg']

        loader.get_from_path(files[0]).AndReturn(None)
        loader.get_from_path(files[1]).AndReturn(None)

        self.mox.ReplayAll()

        crawler = avalon.tags.scan.TagCrawler(loader, logger)
        out = crawler.get_tags(files)

        assert 2 == len(out)
        self.mox.VerifyAll()

