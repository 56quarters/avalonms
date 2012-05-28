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

import errno
import grp
import os
import pwd
import resource
import threading


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
    'is_perm_error',
    'is_pid_alive'
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
    if not hasattr(e, 'errno'):
        return False
    return e.errno in (errno.EACCES, errno.EPERM)


def is_pid_alive(pid):
    """Return true if the given pid is running, false otherwise."""
    try:
        os.kill(pid, 0)
    except OSError, e:
        if errno.EINVAL == e.errno:
            raise
        if errno.ESRCH == e.errno:
            return False
    return True
