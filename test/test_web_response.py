# -*- coding: utf-8 -*-
#

from __future__ import absolute_import, unicode_literals

import uuid

from flask import Flask

import pytest
import avalon.exc
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


@pytest.fixture
def flask_app():
    app = Flask(__name__)
    app.json_decoder = avalon.web.response.AvalonJsonDecoder
    app.json_encoder = avalon.web.response.AvalonJsonEncoder
    return app


def test_render_both_non_none():
    """Ensure that we get an error when trying to render a success
    and error result.
    """
    results = {'foo': 'bar'}
    error = avalon.exc.InvalidParameterNameError(
        'Invalid parameter name', param='foo')

    with pytest.raises(ValueError):
        avalon.web.response.render(results=results, error=error)


def test_render_results(flask_app):
    """Make sure that we can render a success payload correctly."""
    results = {'foo': 'bar'}

    with flask_app.test_request_context('/'):
        response = avalon.web.response.render(results=results)
        assert 'foo'.encode(response.charset) in response.get_data()
        assert 'bar'.encode(response.charset) in response.get_data()


def test_render_errors(flask_app):
    """Make sure that we can render errors correctly."""
    error = avalon.exc.InvalidParameterNameError(
        'Invalid parameter name', param='foo')

    with flask_app.test_request_context('/'):
        response = avalon.web.response.render(error=error)
        assert ('avalon.service.error.invalid_input_name'.encode(response.charset)
                in response.get_data())
