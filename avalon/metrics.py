# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#

"""Utilities for timing method execution.

The purpose of this module is to allow us to easily add timing
information to method calls with a decorator but still be able to
configure the stats client after the decorator has already been
applied.
"""

from __future__ import absolute_import, unicode_literals
import functools


class MetricsBridge(object):
    """Simple holder class for a :class:`statsd.StatsClient` instance.

    This class exists so that we can set up decorators to record metric
    counts ands timings before we've actually configured the statsd client
    that we'll be using. Once the client is available, the `client`
    reference is updated and can be used by all consumers of this class.

    This class is meant to be used as a singleton and only modified during
    application bootstrap.

    :ivar statsd.StatsClient client: Statsd client instance
    """

    def __init__(self):
        self.client = None


class MetricsTimer(object):
    """Callable for timing method execution with a stats client.

    Given a reference to a :class:`MetricsBridge`, key, and method,
    record the time taken to execute the method in statsd, falling
    back gracefully if there is no client available.
    """

    def __init__(self, metrics_bridge, key, func):
        """Set the metrics bridge, metric or timing key, and function.

        :param MetricsBridge metrics_bridge: Bridge for access to a stats
            client to be loaded in the future.
        :param basestring key: Key to record the timing under in Statsd
        :param callable func: Method to invoke and time
        """
        self._bridge = metrics_bridge
        self._key = key
        self._func = func

    def __call__(self, *args, **kwargs):
        """Return the results wrapped method and time its execution.

        If there is no stats client available, return the results of
        the wrapped method without timing its execution.
        """
        client = self._bridge.client
        if client is None:
            return self._func(*args, **kwargs)

        with client.timer(self._key):
            return self._func(*args, **kwargs)


def timed(key):
    """Get a new decorator for recording method execution time.

    The execution time will be recorded under ``key`` in Statsd
    in milliseconds. Note that this requires that the singleton
    `bridge` instance is updated with a correctly configured
    stats client.

    Note that although the type of the key is `basestring` it must
    be a str or unicode type that contains only ASCII characters

    :param basestring key: Key to record timing results under
    :return: decorator for recording method execution time
    :rtype: callable
    """

    def decorator(func):
        timer = MetricsTimer(bridge, key, func)

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return timer(*args, **kwargs)

        return wrapped

    return decorator


bridge = MetricsBridge()
