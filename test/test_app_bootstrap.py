# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals

from flask import Config
import avalon.app.bootstrap


def test_build_config():
    """Ensure that our use of pkgutil works in all supported Python versions."""
    config = avalon.app.bootstrap.build_config()
    assert isinstance(config, Config), "Did not get expected flask.Config instance"
    assert 'avalon.error' == config['LOGGER_NAME'], "Did not get expected config value"
