# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals
import mock
from nose.tools import raises

import avalon.models
import avalon.exc
from sqlalchemy.exc import ArgumentError


@raises(avalon.exc.ConnectionError)
def test_get_engine_malformed_url():
    """Make sure invalid URLs are translated to connection errors."""
    create_engine = mock.Mock()
    create_engine.side_effect = ArgumentError("Cannot parse URL")
    avalon.models.get_engine('foo', factory=create_engine)


@raises(avalon.exc.ConnectionError)
def test_get_engine_unsupported_adapter():
    """Make sure unsupported database adapters are translated to connection errors."""
    create_engine = mock.Mock()
    create_engine.side_effect = ImportError("No such adapter")
    avalon.models.get_engine('mysql://something/else', factory=create_engine)


def test_get_engine_success():
    """Make sure we return a proper engine if there are no issues with the URL."""
    create_engine = mock.Mock()
    engine = avalon.models.get_engine('sqlite:////dev/null', factory=create_engine)
    assert engine is not None, "Got unexpected 'None' engine"
