# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 TSH Labs <projects@tshlabs.org>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


""" Miscellaneous utility functions and classes.
"""

import grp
import itertools
import os
import pwd
import resource
import sys
import threading


__all__ = [
    'get_uid',
    'get_gid',
    'get_uname',
    'get_gname',
    'get_current_uname',
    'get_current_gname',
    'get_dict_size',
    'get_set_size',
    'get_mem_usage',
    'get_thread_names'
    ]


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


def get_dict_size(o):
    """Get the memory used by a dictionary in bytes.

    Examine the dictionary recursively suming the size of any
    other dictionaries and sets contained in the given dictionary.
    """
    size = sys.getsizeof(o)
    seen = set()

    for thing in itertools.chain.from_iterable(o.items()):
        thing_id = id(thing)
        if thing_id in seen:
            continue

        if isinstance(thing, dict):
            size += get_dict_size(thing)
        elif isinstance(thing, set):
            size += get_set_size(thing)
        else:
            size += sys.getsizeof(thing)
        seen.add(thing_id)
    return size


def get_set_size(o):
    """Get the memory used by a set in bytes."""
    size = sys.getsizeof(o)
    for thing in o:
        size += sys.getsizeof(thing)
    return size


def get_mem_usage():
    """Return the current memory usage of the process in MB."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def get_thread_names():
    """Get the names of all running threads."""
    return [t.name for t in threading.enumerate()]
