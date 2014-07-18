# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals

import uuid

import avalon.web.response

from avalon.compat import to_uuid_input
from avalon.elms import IdNameElm


class TestAvalonJsonEncoder(object):
    def test_id_name_elm_rendered_correctly(self):
        """Ensure UUIDs in IdNameElm objects are rendered correctly."""
        elm = IdNameElm(
            id=uuid.UUID(to_uuid_input('7655e605-6eaa-40d8-a25f-5c6c92a4d31a')),
            name='Test Name')

        encoder = avalon.web.response.AvalonJsonEncoder()
        json = encoder.encode(elm)

        assert json.startswith('{')
        assert json.endswith('}')
        assert '7655e605-6eaa-40d8-a25f-5c6c92a4d31a' in json
        assert 'Test Name' in json

    def test_api_error_code_rendered_correctly(self):
        """Ensure our API error objects are rendered correctly."""
        err = avalon.web.response.ApiErrorCode()
        err.code = 100
        err.message = 'Uh oh'
        err.message_key = 'service.errors.uh_oh'
        err.payload = {
            'foo': 'bar'
        }

        encoder = avalon.web.response.AvalonJsonEncoder()
        json = encoder.encode(err)

        assert json.startswith('{')
        assert json.endswith('}')
        assert '100' in json
        assert 'Uh oh' in json
        assert 'service.errors.uh_oh' in json
        assert 'foo' in json
        assert 'bar' in json
