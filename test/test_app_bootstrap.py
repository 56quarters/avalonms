# -*- coding: utf-8 -*-
#

from __future__ import absolute_import, unicode_literals

import pytest
from flask import Config
import avalon.app.bootstrap


def test_build_config():
    """Ensure that our use of pkgutil works in all supported Python versions."""
    config = avalon.app.bootstrap.build_config()
    assert isinstance(config, Config), "Did not get expected flask.Config instance"
    assert 'avalon.error' == config['LOGGER_NAME'], "Did not get expected config value"


class TestEndpointPathResolver(object):
    def test_call_base_not_start_with_slash(self):
        resolver = avalon.app.bootstrap._EndpointPathResolver("avalon")

        with pytest.raises(ValueError):
            resolver("songs")

    def test_call_base_is_just_slash_single_part(self):
        resolver = avalon.app.bootstrap._EndpointPathResolver("/")

        assert "/albums" == resolver("albums")

    def test_call_base_is_just_slash_multiple_parts(self):
        resolver = avalon.app.bootstrap._EndpointPathResolver("/")

        assert "/json/albums" == resolver("json/albums")

    def test_call_base_ends_with_slash(self):
        resolver = avalon.app.bootstrap._EndpointPathResolver("/avalon/")

        with pytest.raises(ValueError):
            resolver("artists")

    def test_call_success_single_part(self):
        resolver = avalon.app.bootstrap._EndpointPathResolver("/avalon")

        assert "/avalon/genres" == resolver("genres")

    def test_call_success_multiple_parts(self):
        resolver = avalon.app.bootstrap._EndpointPathResolver("/avalon")

        assert "/avalon/api/songs" == resolver("api/songs")
