# -*- coding: utf-8 -*-
#

from __future__ import absolute_import, unicode_literals
import uuid

import pytest
import avalon.exc
import avalon.web.request


class DummyRequest(object):
    def __init__(self):
        self.args = None


class TestParameters(object):
    def setup(self):
        self.request = DummyRequest()

    def test_get_invalid(self):
        """Ensure a bogus named parameter causes an exception."""
        self.request.args = {}
        r = avalon.web.request.Parameters(self.request)

        with pytest.raises(KeyError):
            r.get("asdf")

    def test_get_missing(self):
        """Ensure a missing valid parameter results in a default
        value.
        """
        self.request.args = {}
        r = avalon.web.request.Parameters(self.request)
        val = r.get('artist', default=None)
        assert val is None

    def test_get_list_val(self):
        """Ensure a parameter with a list value causes an
        exception.
        """
        self.request.args = {'artist': ['a', 'b']}
        r = avalon.web.request.Parameters(self.request)

        with pytest.raises(avalon.exc.InvalidParameterTypeError):
            r.get('artist')

    def test_get_success(self):
        """Test the success case of getting a valid non-list value \
        from the request parameters.
        """
        self.request.args = {'album': 'Dookie'}
        r = avalon.web.request.Parameters(self.request)
        val = r.get('album')
        assert 'Dookie' == val

    def test_get_int_missing(self):
        """Ensure a missing valid parameter results in a default value."""
        self.request.args = {}
        r = avalon.web.request.Parameters(self.request)
        val = r.get_int('limit')
        assert None is val

    def test_get_int_invalid(self):
        """Ensure an invalid value results in an exception."""
        self.request.args = {'limit': 'asdf'}
        r = avalon.web.request.Parameters(self.request)

        with pytest.raises(avalon.exc.InvalidParameterTypeError):
            r.get_int('limit')

    def test_get_int_success(self):
        """Ensure that a valid value gets converted to an int."""
        self.request.args = {'limit': '12'}
        r = avalon.web.request.Parameters(self.request)
        val = r.get_int('limit')
        assert 12 == val

    def test_get_uuid_missing(self):
        """Ensure that a valid missing parameter results in a default value."""
        self.request.args = {}
        r = avalon.web.request.Parameters(self.request)
        val = r.get_uuid('artist_id')
        assert None is val

    def test_get_uuid_invalid(self):
        """Ensure that an invalid value for a UUID field results in an \
        exception."""
        self.request.args = {'artist_id': 'asdf'}
        r = avalon.web.request.Parameters(self.request)

        with pytest.raises(avalon.exc.InvalidParameterTypeError):
            r.get_uuid('artist_id')

    def test_get_uuid_success(self):
        """Ensure that a valid UUID value is converted to a UUID."""
        self.request.args = {'artist_id': 'e4228e96-c165-4a83-a145-038df58f9c8c'}
        r = avalon.web.request.Parameters(self.request)
        val = r.get_uuid('artist_id')
        expected = uuid.UUID('e4228e96-c165-4a83-a145-038df58f9c8c')
        assert expected == val
