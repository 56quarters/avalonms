# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""CLI entry points associated with the Avalon Music Server."""

from __future__ import absolute_import, print_function, unicode_literals

import signal
import sys

import avalon.compat


def install_sigint_handler():
    """Install a simple signal handler to quietly exit on SIGINT."""

    def handler(signum, _):
        print("Exiting on signal {0}...".format(signum), file=sys.stderr)
        sys.exit(1)

    signal.signal(signal.SIGINT, handler)


def input_to_text(s):
    """Convert the given byte string or text type to text using the
    file system encoding of the current system.

    :param basestring s: String or text type to convert
    :return: The string as text
    :rtype: unicode
    """
    return avalon.compat.to_text(s, sys.getfilesystemencoding())
