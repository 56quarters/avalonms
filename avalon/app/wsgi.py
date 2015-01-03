# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Expose a configured, WSGI compatible application.

By default the application will attempt to read the path of an installation
specific configuration file from the :data:`AVALON_CONFIG` environmental
variable.

Note that this module should typically not be imported directly, instead it
is meant to be used by a WSGI application server such as Gunicorn, uWSGI, or
Apache with mod_wsgi. Importing it has the side-effect of bootstrapping the
entire Avalon Music Server application.

This module will run the application using the built in Flask server in debug
mode when invoked as :data:`__main__`. Note that running the Avalon Music Server
like this should NOT BE DONE IN PRODUCTION.
"""

from __future__ import absolute_import, print_function, unicode_literals
import sys

from avalon.app.bootstrap import bootstrap, CONFIG_ENV_VAR


__all__ = [
    'application'
]

try:
    # Handle keyboard interrupts during bootstrap quietly by
    # just exiting. This has the added benefit of handling uWSGI
    # trying to shutdown while the application is still starting
    # up since it uses SIGINT for stopping the server.
    # pylint: disable=invalid-name
    application = bootstrap(config_env=CONFIG_ENV_VAR)
except KeyboardInterrupt:
    print("Caught SIGINT during bootstrap, exiting", file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    application.run(debug=True, use_reloader=False)
