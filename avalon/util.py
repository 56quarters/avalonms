# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


"""Miscellaneous utility functions and classes."""

import errno
import grp
import pwd
import resource
import threading

import os


__all__ = [
    'are_root',
    'get_uid',
    'get_gid',
    'get_uname',
    'get_gname',
    'get_current_uname',
    'get_current_gname',
    'get_mem_usage',
    'get_thread_names',
    'is_perm_error'
]


def are_root():
    """Return true if we are super user (or in wheel)."""
    return 0 == os.geteuid() or 0 == os.getegid()


def get_uid(user_name):
    """Get the user ID of the given user name."""
    try:
        return pwd.getpwnam(user_name).pw_uid
    except KeyError:
        return None


def get_gid(group_name):
    """Get the group ID of the given group name."""
    try:
        return grp.getgrnam(group_name).gr_gid
    except KeyError:
        return None


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


def get_mem_usage():
    """Return the current memory usage of the process in MB."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def get_thread_names():
    """Get the names of all running threads."""
    return [t.name for t in threading.enumerate()]


def is_perm_error(e):
    """Return true if this exception is file permission related."""
    try:
        return e.errno in (errno.EACCES, errno.EPERM)
    except AttributeError:
        return False


