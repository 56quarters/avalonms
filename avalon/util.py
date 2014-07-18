# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Miscellaneous utility functions and classes."""

from __future__ import unicode_literals
import errno
import grp
import pwd
import resource

import os


__all__ = [
    'get_mem_usage',
    'is_perm_error',
    'get_current_gname',
    'get_current_uname',
    'get_gname',
    'get_uname'
]


def get_mem_usage():
    """Return the current memory usage of the process in MB.

    :return: Memory usage of the current process in MB
    :rtype: float
    """
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def is_perm_error(e):
    """Return true if this exception is file permission related.

    :param EnvironmentalError e: Exception to test for permission issues
    :return: True if the exception is permission related, false otherwise
    :rtype: bool
    """
    try:
        return e.errno in (errno.EACCES, errno.EPERM)
    except AttributeError:
        return False


def get_uname(uid):
    """Get the user name from the user ID."""
    try:
        return pwd.getpwuid(uid).pw_name
    except KeyError:
        return None


def get_gname(gid):
    """Get the group name from the group ID."""
    try:
        return grp.getgrgid(gid).gr_name
    except KeyError:
        return None


def get_current_uname():
    """Get the name of the current processes effective user."""
    return get_uname(os.geteuid())


def get_current_gname():
    """Get the name of the current processes effective group."""
    return get_gname(os.getegid())
