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

import argparse
import os
import os.path
import socket
import tempfile

import avalon.util


__all__ = [
    'ScanAppDefaults',
    'ScanAppConfig',
    'ServerAppDefaults',
    'ServerAppConfig',
    'CollectionAction',
    'IpAddressAction',
    'DaemonUserAction',
    'DaemonGroupAction',
    'ServerPortAction',
    'ServerQueueAction',
    'ServerThreadsAction'
    ]


class CollectionAction(argparse.Action):

    """Validation for the path to the music collection."""

    def __call__(self, parser, namespace, values, option_string=None):
        if not values or not os.path.exists(values):
            raise ValueError(
                "That doesn't appear to be a valid music "
                "collection path")
        setattr(namespace, self.dest, values)


class IpAddressAction(argparse.Action):

    """Validation for the address to bind the server to."""

    def __call__(self, parser, namespace, values, option_string=None):
        if not _is_valid_addr(values):
            raise ValueError(
                "That doesn't appear to be a valid "
                "interface address")
        setattr(namespace, self.dest, values)


class DaemonUserAction(argparse.Action):
    
    """Validation for a user for the daemon to switch to."""

    def __call__(self, parser, namespace, values, option_string=None):
        if not _is_valid_user(values):
            raise ValueError(
                "You must specify a valid daemon user")
        setattr(namespace, self.dest, values)


class DaemonGroupAction(argparse.Action):

    """Validation for a group for the daemon to switch to."""
    
    def __call__(self, parser, namespace, values, option_string=None):
        if not _is_valid_group(values):
            raise ValueError(
                "You must specify a valid daemon group")
        setattr(namespace, self.dest, values)


class ServerPortAction(argparse.Action):
    
    """Validation for the port for the server to run on."""

    def __call__(self, parser, namespace, values, option_string=None):
        val = _validate_int('port number', values)
        setattr(namespace, self.dest, val)


class ServerQueueAction(argparse.Action):

    """Validation for the connection queue size for the server."""
    
    def __call__(self, parser, namespace, values, option_string=None):
        val = _validate_int('queue size', values)
        setattr(namespace, self.dest, val)


class ServerThreadsAction(argparse.Action):

    """Validation for the number threads to use for the server."""
    
    def __call__(self, parser, namespace, values, option_string=None):
        val = _validate_int('number of threads', values)
        setattr(namespace, self.dest, val)


def _validate_int(field_name, val):
    """Ensure that the given value is a positive integer."""
    try:
        val = int(val)
    except ValueError:
        raise ValueError('The %s must be a positive integer' % field_name)
    if val <= 0:
        raise ValueError('The %s must be a positive integer' % field_name)
    return val


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


class ServerAppDefaults(object):

    """Compute default values for server configuration options."""

    def __init__(self):
        """Set defaults for all arguments or options."""
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


class ScanAppDefaults(object):

    """Compute default values for scanner configuration options."""

    def __init__(self):
        """Set defaults for all arguments or options."""
        self.collection = None
        self.db_path = os.path.join(tempfile.gettempdir(), 'avalon.sqlite')


class _AppConfig(object):

    """Base class for accessing user input and default values."""

    def __init__(self, parser, defaults):
        """Set the argument parser and default values."""
        self._parser = parser
        self._defaults = defaults
        self._options = None

    def validate(self):
        """Perform addition validation for the input."""
        raise NotImplementedError()

    def _parse(self):
        """Parse user input and store the results."""
        self._options = self._parser.parse_args()

    def __getattr__(self, name):
        """Get a configuration value or object attribute.
        Prefer:
        * Object attributes
        * User input
        * Default values
        """
        try:
            return self.__getattribute__(name)
        except AttributeError:
            pass

        opt = getattr(self._options, name, None)
        if opt is not None:
            return opt

        if hasattr(self._defaults, name):
            return getattr(self._defaults, name)

        raise AttributeError('No such attribute or config setting "%s"' % name)


class ServerAppConfig(_AppConfig):

    """Validation for configuration options."""

    def validate(self):
        """Validation for options that can't be validated individually
        using custom Action classes via argparse.
        """
        self._parse()

        if self.access_log is None and self.daemon:
            raise ValueError(
                "You must specify an access log in daemon mode")

        if self.error_log is None and self.daemon:
            raise ValueError(
                "You must specify an error log in daemon mode")
        
        
class ScanAppConfig(_AppConfig):
    """ """

    def validate(self):
        """ """
        self._parse()

