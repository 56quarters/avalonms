# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Default configuration settings for the Avalon Music Server"""

from __future__ import absolute_import, unicode_literals
import logging
from tempfile import gettempdir

from os.path import join
from avalon.log import DEFAULT_LOGGER_NAME


# Database connection string for storing or reading music meta data. By
# default a local SQLite database is used.
DATABASE_URL = 'sqlite:///' + join(gettempdir(), 'avalon.sqlite')


# Flask will "pretty print" JSON output by default, we would rather it
# didn't do that. You probably don't really want to change this.
JSONIFY_PRETTYPRINT_REGULAR = False


# Format to use for dates or timestamps in log messages. If you wish to
# change this format see http://docs.python.org/2/library/time.html#time.strftime
# for an explanation of the format and more information
LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


# Format for messages logged by the Avalon Music Server. For all available
# options see http://docs.python.org/2/library/logging.html#logrecord-attributes
LOG_FORMAT = '[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s'


# How verbose should logging be? By default we log all INFO and
# more severe level messages. For all possible values take a look
# at the 'logging' module. If you've ever used it before you can
# probably guess: DEBUG, INFO, WARN, ERROR, and CRITICAL.
LOG_LEVEL = logging.INFO


# Path to the log file. If the path is set to None, logging will be
# written to STDERR. The log will be opened in append mode and will
# not be rotated by the Avalon Music Server. It should be owned by
# the user the server will run as. Depending on the application
# container you use the ownership may be changed for you. When/if the
# log file is rotated by an external process the server may need to
# be reloaded to start making use of the new log file. This will be
# specific to the server you are using.
LOG_PATH = None


# Name of the logger to use for all application logging. You probably
# don't want to change this. Really, this just ensures that the Flask
# portion of the application is using the same logging as the rest of
# the server.
LOGGER_NAME = DEFAULT_LOGGER_NAME


# Configuration for logging unexpected errors to a centralized
# third-party error aggregation service. Enabling this logging
# requires supplying a Sentry DSN configuration string below and
# installing the Raven Sentry client (`pip install raven`).
# See https://www.getsentry.com/docs/ for more information.
SENTRY_DSN = None


# Hostname to write Statsd timers and counters to if there is a
# client installed. The expected client will discard any errors
# encountered when trying to write metrics so setting this value
# to a host not running the Statsd daemon is equivalent to
# disabling it.
STATSD_HOST = 'localhost'


# Port to write Statsd timers and counters to. Port 8125 is the
# port that the Etsy Statsd implementation runs on by default.
STATSD_PORT = 8125


# Prefix all metrics emitted with this string. Useful to make
# sure metrics from the Avalon Music Server don't pollute the
# top-level namespace. You may want further split metrics by
# the environment you are running in (dev vs staging vs prod).
# This can be done by adding a dot-separated string to the
# existing prefix, e.g. 'avalon.prd' or 'avalon.dev'.
STATSD_PREFIX = 'avalon'
