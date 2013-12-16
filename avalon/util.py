# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2013 TSH Labs <projects@tshlabs.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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


