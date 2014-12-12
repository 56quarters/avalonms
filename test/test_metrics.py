# -*- coding: utf-8 -*-
#

from __future__ import absolute_import, unicode_literals
import mock

import pytest
import avalon.metrics


@pytest.fixture
def bridge():
    return avalon.metrics.MetricsBridge()


@pytest.fixture
def client():
    return mock.MagicMock()


@pytest.fixture
def wrapped():
    return mock.Mock()


class TestMetricsTimer(object):
    def test_call_no_client(self, bridge, wrapped):
        """Test that the wrapped method is called even with no client configured."""
        bridge.client = None
        timer = avalon.metrics.MetricsTimer(bridge, 'foo.bar', wrapped)
        timer(123, 'abc')

        wrapped.assert_called_with(123, 'abc')

    def test_call_with_client(self, bridge, client, wrapped):
        """Test that the wrapped method is called and timed with a client."""
        bridge.client = client
        timer = avalon.metrics.MetricsTimer(bridge, 'foo.bar', wrapped)
        timer(123, 'abc')

        wrapped.assert_called_with(123, 'abc')
        assert client.timer.called, "Expected timer to be called"


def test_timed_client_called(monkeypatch, client):
    monkeypatch.setattr(avalon.metrics.bridge, 'client', client)

    @avalon.metrics.timed('some.method')
    def some_method(foo, bar):
        return foo + bar

    res = some_method(123, 456)

    assert 579 == res, "Did not get expected output from wrapped method"
    client.timer.assert_called_with('some.method')
