# -*- coding: utf-8 -*-
#

import re
from datetime import datetime

import mox
import pytest

import avalon.tags.read


class TagpyMock(object):
    def FileRef(self, path):
        pass


class TagpyFileMock(object):
    def tag(self):
        pass
    def audioProperties(self):
        pass


class TagpyTagMock(object):
    def __init__(self):
        self.album = None
        self.artist = None
        self.genre = None
        self.title = None
        self.track = None
        self.year = None


class TagpyAudioPropertiesMock(object):
    def __init__(self):
        self.length = None


class MutagenMock(object):
    def File(self, path, easy=False):
        pass


class MutagenFileMock(object):
    def __init__(self):
        self.info = None
    def get(self, key):
        pass


class MutagenAudioMock(object):
    def __init__(self):
        self.length = None


class TestReadTagpy(object):

    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_unicode_error(self):
        tagpy = self.mox.CreateMock(TagpyMock)
        tagpy.FileRef(mox.IsA(str)).AndRaise(
            UnicodeDecodeError("utf-8", "blah", 0, 0, "blah"))

        self.mox.ReplayAll()

        with pytest.raises(IOError):
            avalon.tags.read.read_tagpy(u'/path/file', tagpy)
        self.mox.VerifyAll()

    def test_value_error(self):
        tagpy = self.mox.CreateMock(TagpyMock)
        tagpy.FileRef(mox.IsA(str)).AndRaise(
            ValueError("Invalid file blah"))

        self.mox.ReplayAll()

        with pytest.raises(IOError):
            avalon.tags.read.read_tagpy(u'/path/file', tagpy)
        self.mox.VerifyAll()

    def test_invalid_tag(self):
        tagpy = self.mox.CreateMock(TagpyMock)
        file_ref = self.mox.CreateMock(TagpyFileMock)

        tagpy.FileRef(mox.IsA(str)).AndReturn(file_ref)
        file_ref.tag().AndReturn(None)

        self.mox.ReplayAll()

        with pytest.raises(IOError):
            avalon.tags.read.read_tagpy(u'/path/file', tagpy)
        self.mox.VerifyAll()

    def test_success(self):
        tagpy = self.mox.CreateMock(TagpyMock)
        file_ref = self.mox.CreateMock(TagpyFileMock)
        tag = self.mox.CreateMock(TagpyTagMock)

        tagpy.FileRef(mox.IsA(str)).AndReturn(file_ref)
        file_ref.tag().AndReturn(tag)

        self.mox.ReplayAll()

        assert file_ref == avalon.tags.read.read_tagpy(u'/path/file', tagpy)
        self.mox.VerifyAll()


class TestReadMutagen(object):

    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_unicode_error(self):
        mutagen = self.mox.CreateMock(MutagenMock)
        mutagen.File(mox.IsA(str), easy=True).AndRaise(
            UnicodeDecodeError("utf-8", "blah", 0, 0, "blah"))

        self.mox.ReplayAll()

        with pytest.raises(IOError):
            avalon.tags.read.read_mutagen(u'/path/file', mutagen)
        self.mox.VerifyAll()

    def test_ioerror(self):
        mutagen = self.mox.CreateMock(MutagenMock)
        mutagen.File(mox.IsA(str), easy=True).AndRaise(
            IOError("No such file"))

        self.mox.ReplayAll()

        with pytest.raises(IOError):
            avalon.tags.read.read_mutagen(unicode('/path/file'), mutagen)
        self.mox.VerifyAll()

    def test_invalid_tag(self):
        mutagen = self.mox.CreateMock(MutagenMock)
        mutagen.File(mox.IsA(str), easy=True).AndReturn(None)

        self.mox.ReplayAll()

        with pytest.raises(IOError):
            avalon.tags.read.read_mutagen(unicode('/path/file'), mutagen)
        self.mox.VerifyAll()

    def test_success(self):
        mutagen = self.mox.CreateMock(MutagenMock)
        file_ref = self.mox.CreateMock(MutagenFileMock)
        mutagen.File(mox.IsA(str), easy=True).AndReturn(file_ref)

        self.mox.ReplayAll()

        assert file_ref == avalon.tags.read.read_mutagen(u'/path/file', mutagen)
        self.mox.VerifyAll()


class TestMetadataDateParser(object):

    def test_is_digit(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
        assert 2001 == parser.parse(u'2001')

    def test_is_timestamp(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)
        assert 2001 == parser.parse(u'2001-01-01T14:01:59')

    def test_is_invalid(self):
        parser = avalon.tags.read.MetadataDateParser(datetime.strptime)

        with pytest.raises(ValueError):
            parser.parse('Something')


class TestMetadataTrackParser(object):

    def test_is_digit(self):
        parser = avalon.tags.read.MetadataTrackParser(re.match)
        assert 1 == parser.parse(u'1')

    def test_is_fraction(self):
        parser = avalon.tags.read.MetadataTrackParser(re.match)
        assert 2 == parser.parse(u'2/5')

    def test_is_invalid(self):
        parser = avalon.tags.read.MetadataTrackParser(re.match)

        with pytest.raises(ValueError):
            parser.parse(u'Blah')


class TestFromTagpy(object):

    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_invalid_track(self):
        audio = TagpyAudioPropertiesMock()
        audio.length = 123

        tag = TagpyTagMock()
        tag.album = u'blah'
        tag.artist = u'blah'
        tag.genre = u'blah'
        tag.title = u'blah'
        tag.track = u'asdf'
        tag.year = u'2012'

        path = u'/path/file'
        file_ref = self.mox.CreateMock(TagpyFileMock)
        file_ref.tag().AndReturn(tag)
        file_ref.audioProperties().AndReturn(audio)

        self.mox.ReplayAll()

        with pytest.raises(ValueError):
            avalon.tags.read.from_tagpy(path, file_ref)

    def test_invalid_year(self):
        audio = TagpyAudioPropertiesMock()
        audio.length = 123

        tag = TagpyTagMock()
        tag.album = u'blah'
        tag.artist = u'blah'
        tag.genre = u'blah'
        tag.title = u'blah'
        tag.track = u'1'
        tag.year = u'asdf'

        path = u'/path/file'
        file_ref = self.mox.CreateMock(TagpyFileMock)
        file_ref.tag().AndReturn(tag)
        file_ref.audioProperties().AndReturn(audio)

        self.mox.ReplayAll()

        with pytest.raises(ValueError):
            avalon.tags.read.from_tagpy(path, file_ref)

    def test_invalid_length(self):
        audio = TagpyAudioPropertiesMock()
        audio.length = 'asdf'

        tag = TagpyTagMock()
        tag.album = u'blah'
        tag.artist = u'blah'
        tag.genre = u'blah'
        tag.title = u'blah'
        tag.track = u'1'
        tag.year = u'2012'

        path = u'/path/file'
        file_ref = self.mox.CreateMock(TagpyFileMock)
        file_ref.tag().AndReturn(tag)
        file_ref.audioProperties().AndReturn(audio)

        self.mox.ReplayAll()

        with pytest.raises(ValueError):
            avalon.tags.read.from_tagpy(path, file_ref)

    def test_success(self):
        audio = TagpyAudioPropertiesMock()
        audio.length = 134

        tag = TagpyTagMock()
        tag.album = u'Dookie'
        tag.artist = u'Green Day'
        tag.genre = u'Punk'
        tag.title = u'She'
        tag.track = u'8'
        tag.year = u'1994'

        path = u'/path/file'
        file_ref = self.mox.CreateMock(TagpyFileMock)
        file_ref.tag().AndReturn(tag)
        file_ref.audioProperties().AndReturn(audio)

        self.mox.ReplayAll()

        meta = avalon.tags.read.from_tagpy(path, file_ref)
        assert 134 == meta.length
        assert u'Dookie' == meta.album
        assert u'Green Day' == meta.artist
        assert u'Punk' == meta.genre
        assert u'She' == meta.title
        assert 8 == meta.track
        assert 1994 == meta.year
        self.mox.VerifyAll()


class TestFromMutagen(object):

    def setup_method(self, method):
        self.mox = mox.Mox()

    def teardown_method(self, method):
        self.mox.UnsetStubs()

    def test_invalid_track(self):
        path = u'/path/file'
        audio = self.mox.CreateMock(MutagenAudioMock)
        audio.length = 103
        file_ref = self.mox.CreateMock(MutagenFileMock)
        file_ref.info = audio
        file_ref.get('album').AndReturn([u'Insomniac'])
        file_ref.get('artist').AndReturn([u'Green Day'])
        file_ref.get('genre').AndReturn([u'Punk'])
        file_ref.get('title').AndReturn([u'Brat'])
        file_ref.get('tracknumber').AndReturn([u'asdf'])
        file_ref.get('date').AndReturn([u'1995'])

        self.mox.ReplayAll()

        with pytest.raises(ValueError):
            avalon.tags.read.from_mutagen(path, file_ref)
        # No verification since we don't know if some
        # methods aren't called due to validation errors

    def test_invalid_year(self):
        path = unicode('/path/file')
        audio = self.mox.CreateMock(MutagenAudioMock)
        audio.length = 103
        file_ref = self.mox.CreateMock(MutagenFileMock)
        file_ref.info = audio
        file_ref.get('album').AndReturn([u'Insomniac'])
        file_ref.get('artist').AndReturn([u'Green Day'])
        file_ref.get('genre').AndReturn([u'Punk'])
        file_ref.get('title').AndReturn([u'Brat'])
        file_ref.get('tracknumber').AndReturn([u'2'])
        file_ref.get('date').AndReturn([u'asdf'])

        self.mox.ReplayAll()

        with pytest.raises(ValueError):
            avalon.tags.read.from_mutagen(path, file_ref)
        # No verification since we don't know if some
        # methods aren't called due to validation errors

    def test_none_album(self):
        path = unicode('/path/file')
        audio = self.mox.CreateMock(MutagenAudioMock)
        audio.length = 103
        file_ref = self.mox.CreateMock(MutagenFileMock)
        file_ref.info = audio
        file_ref.get('album').AndReturn(None)
        file_ref.get('artist').AndReturn([u'Green Day'])
        file_ref.get('genre').AndReturn([u'Punk'])
        file_ref.get('title').AndReturn([u'Brat'])
        file_ref.get('tracknumber').AndReturn([u'2'])
        file_ref.get('date').AndReturn([u'1995'])

        self.mox.ReplayAll()

        meta = avalon.tags.read.from_mutagen(path, file_ref)
        assert u'' == meta.album
        self.mox.VerifyAll()

    def test_success(self):
        path = unicode('/path/file')
        audio = self.mox.CreateMock(MutagenAudioMock)
        audio.length = 103
        file_ref = self.mox.CreateMock(MutagenFileMock)
        file_ref.info = audio
        file_ref.get('album').AndReturn([u'Insomniac'])
        file_ref.get('artist').AndReturn([u'Green Day'])
        file_ref.get('genre').AndReturn([u'Punk'])
        file_ref.get('title').AndReturn([u'Brat'])
        file_ref.get('tracknumber').AndReturn([u'2'])
        file_ref.get('date').AndReturn([u'1995'])

        self.mox.ReplayAll()

        meta = avalon.tags.read.from_mutagen(path, file_ref)
        assert 103 == meta.length
        assert u'Insomniac' == meta.album
        assert u'Green Day' == meta.artist
        assert u'Punk' == meta.genre
        assert u'Brat' == meta.title
        assert 2 == meta.track
        assert 1995 == meta.year
        self.mox.VerifyAll()

