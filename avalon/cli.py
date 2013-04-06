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


"""Command line configuration parsing classes."""

import argparse
import os.path
import socket
import tempfile

import avalon.util


__all__ = [
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


class _AppConfig(object):
    """Base class for accessing user input and default values."""

    def __init__(self, parser, defaults):
        """Set the argument parser and default values."""
        self._parser = parser
        self._defaults = defaults
        self._options = None

    def validate(self):
        """Perform addition validation for the input."""
        self._parse()

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
    """Validation for server configuration options."""

    def validate(self):
        """Validation for options that can't be validated individually
        using custom Action classes via argparse.
        """
        super(ServerAppConfig, self).validate()

        if self.access_log is None and self.daemon:
            raise ValueError(
                "You must specify an access log in daemon mode")

        if self.error_log is None and self.daemon:
            raise ValueError(
                "You must specify an error log in daemon mode")

