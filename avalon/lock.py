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


__all__ = []


class AvalonLockFile(object):

    """ """

    def __init__(self, lock_path):
        """ """
        self._path = lock_path
        self._locked = False

    def acquire(self):
        """ """
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

    def _get_pid(self):
        """ """
        pid = -1

        try:
            with open(self._path) as handle:
                pid = int(handle.read().strip())
        except (ValueError, IOError):
            pass
        return pid
        
    def clear_stale(self):
        """ """
        pid = self._get_pid()
        if pid > 0 and avalon.util.is_pid_alive(pid):
            return

        try:
            os.unlink(self._path)
        except OSError:
            pass

    def is_locked(self):
        """ """
        return self._locked

    def release(self):
        """ """
        if not self._locked:
            return
        os.unlink(self._path)
        self._locked = False

    def __enter__(self):
        """ """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ """
        pass

