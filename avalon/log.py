# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Logging initialization and access methods."""

from __future__ import absolute_import, unicode_literals
import logging
import sys

import avalon.exc
import avalon.util


DEFAULT_LOGGER_NAME = "avalon.error"


class AvalonLogConfig(object):
    """Configuration for the logger."""

    def __init__(self):
        self.stream = sys.stderr
        self.path = None
        self.level = None
        self.fmt = None
        self.date_fmt = None


def get_error_log():
    """Get the system-wide Avalon :class:`logging.Logger` instance.

    :return: The system-wide Avalon logger
    :rtype: logging.Logger
    """
    return logging.getLogger(DEFAULT_LOGGER_NAME)


def initialize(logger, config):
    """Set up the system-wide Avalon logger using the given configuration.

    The logging level for the logger will be set and a handler will be added
    that either writes to ``STDERR`` or to a file, depending on the supplied
    configuration.

    :param logging.Logger logger: Logger instance to configure
    :param AvalonLogConfig config: Configuration for the logger
    """
    try:
        if config.path is None:
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = logging.FileHandler(config.path)
    except IOError as e:
        if avalon.util.is_perm_error(e):
            raise avalon.exc.PermissionError(
                'Insufficient permission to create or open log {0}'.format(e.filename))
        raise

    handler.setFormatter(logging.Formatter(config.fmt, config.date_fmt))
    logger.setLevel(config.level)
    logger.addHandler(handler)
