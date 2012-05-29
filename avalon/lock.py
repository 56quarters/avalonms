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


""" """

import errno
import os.path
import tempfile

import avalon.exc
import avalon.util


__all__ = [
    'get_lock_pid',
    'AvalonLockFile'
    ]


class AvalonLockFile(object):

    """ """

    def __init__(self, lock_path):
        """Set the lock file to use"""
        self._path = lock_path
        self._locked = False

    def acquire(self):
        """Acquire a proccess-wide lock using a lock file (hard link)."""
        if self._locked:
            return

        base = os.path.dirname(self._path)
        handle = tempfile.NamedTemporaryFile(dir=base)
        handle.write(str(os.getpid()))

        try:
            os.link(handle.name, self._path)
        except OSError, e:
            if errno.EEXIST == e.errno:
                raise avalon.exc.AlreadyLockedError(
                    'File [%s] appears to be locked already' % self._path)
            raise
        else:
            self._locked = True
        finally:
            handle.close()

    def clear_stale(self):
        """Attempt to remove an existing lock file if it is stale."""
        pid = get_lock_pid(self._path)
        # If the lock file existed and there was a valid PID
        # in it check if the process is still running and abort
        # if so.
        if pid > 0 and avalon.util.is_pid_alive(pid):
            return

        try:
            os.unlink(self._path)
        except OSError:
            pass

    def is_locked(self):
        """Return true if the lock has been acquired, false otherwise."""
        return self._locked

    def release(self):
        """Release the lock if it has been acquired."""
        if not self._locked:
            return
        os.unlink(self._path)
        self._locked = False

    def __enter__(self):
        """ """
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ """
        self.release()
        return False


def get_lock_pid(path):
    """Get the pid in an existing lock file, -1 if there is no
    such file or it does not contain a valid PID."""
    pid = -1
    try:
        with open(path, 'rb') as handle:
            pid = int(handle.read().strip())
    except (ValueError, IOError):
        pass
    return pid
