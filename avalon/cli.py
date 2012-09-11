# -*- coding: utf-8 -*-
#
# Avalon Music Server
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


"""Command line configuration parsing classes."""


import os
import os.path
import socket
import tempfile

import avalon.util


__all__ = [
    'DefaultConfig',
    'ApplicationConfig'
    ]


def _is_valid_addr(addr):
    """Return true if this is a valid IPv4 or IPv6 address, false
    otherwise.
    """
    protos = [socket.AF_INET]
    if socket.has_ipv6:
        protos.append(socket.AF_INET6)

    for proto in protos:
        try:
            socket.inet_pton(proto, addr)
        except socket.error:
            pass
        else:
            return True
    return False


def _is_valid_user(user):
    """Return true if this a valid user name, false otherwise."""
    return avalon.util.get_uid(user) is not None


def _is_valid_group(group):
    """Return true if this a valid group name, false otherwise."""
    return avalon.util.get_gid(group) is not None


class DefaultConfig(object):

    """Compute default values for configuration options."""

    def __init__(self):
        """ Set defaults for all arguments or options."""
        self.collection = None
        self.access_log = None
        self.daemon = False
        self.daemon_user = avalon.util.get_current_uname()
        self.daemon_group = avalon.util.get_current_gname()
        self.db_path = os.path.join(tempfile.gettempdir(), 'avalon.sqlite')
        self.error_log = None
        self.no_scan = False
        self.server_address = socket.gethostbyname('localhost')
        self.server_port = 8080
        self.server_queue = 4
        self.server_threads = 4


class ApplicationConfig(object):

    """Validation for configuration options."""

    def __init__(self, opts, defaults):
        """Initialize input to default values and then
        override it if there is a user supplied value.
        """
        self.collection = defaults.collection
        self.access_log = defaults.access_log
        self.daemon = defaults.daemon
        self.daemon_user = defaults.daemon_user
        self.daemon_group = defaults.daemon_group
        self.db_path = defaults.db_path
        self.error_log = defaults.error_log
        self.no_scan = defaults.no_scan
        self.server_address = defaults.server_address
        self.server_port = defaults.server_port
        self.server_queue = defaults.server_queue
        self.server_threads = defaults.server_threads

        self._set_overrides(opts)

    def _set_overrides(self, opts):
        """Override default values with user supplied values
        if provided.
        """
        for attr in dir(opts):
            if attr.startswith('_'):
                continue
            val = getattr(opts, attr)
            if val is None:
                continue
            setattr(self, attr, val)

    def validate(self):
        """Validate user input values or default values. Raise
        a ValueError for any invalid input.
        """
        if not self.collection or not os.path.exists(self.collection):
            raise ValueError(
                "That doesn't appear to be a valid music collection path")

        if self.access_log is None and self.daemon:
            raise ValueError(
                "You must specify an access log in daemon mode")

        if self.error_log is None and self.daemon:
            raise ValueError(
                "You must specify an error log in daemon mode")

        if not _is_valid_user(self.daemon_user) and self.daemon:
            raise ValueError(
                "You must specify a valid daemon user")

        if not _is_valid_group(self.daemon_group) and self.daemon:
            raise ValueError(
                "You must specify a valid daemon group")

        if not _is_valid_addr(self.server_address):
            raise ValueError(
                "That doesn't appear to be a valid interface address")
            
        try:
            self.server_port = int(self.server_port)
        except ValueError:
            raise ValueError("That doesn't appear to be a valid port")

        if 0 >= self.server_port:
            raise ValueError("The port for the server must be positive")

        try:
            self.server_queue = int(self.server_queue)
        except ValueError:
            raise ValueError(
                "That doesn't appear to be a valid queue size")

        if 0 >= self.server_queue:
            raise ValueError("The queue size must be positive")

        try:
            self.server_threads = int(self.server_threads)
        except ValueError:
            raise ValueError(
                "That doesn't appear to be a valid number of threads")

        if 0 >= self.server_threads:
            raise ValueError("The number of threads to use must be positive")

