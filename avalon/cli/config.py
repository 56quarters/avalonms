# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Print the default configuration for the Avalon Music Server."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import pkgutil
import sys

import os.path
import avalon
import avalon.app.factory
import avalon.log
from avalon.app.bootstrap import build_config, CONFIG_ENV_VAR
from avalon.cli import install_sigint_handler


def get_opts(prog):
    parser = argparse.ArgumentParser(
        prog=prog,
        description=__doc__)

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=avalon.__version__,
        help='Show the version of the Avalon Music Server and exit')

    return parser.parse_args()


def main():
    install_sigint_handler()
    prog = os.path.basename(sys.argv[0])
    # We're not interested in the return value here, we're just
    # using argparse to handle --help and --version options, we
    # don't actually need any arguments to run this script.
    _ = get_opts(prog)

    config = build_config(env_var=CONFIG_ENV_VAR)
    logger = avalon.log.get_error_log()
    avalon.app.factory.configure_logger(logger, config)

    loader = pkgutil.find_loader('avalon.settings')
    if loader is None:
        logger.error(
            "%s: could not find a loader for default settings module", prog)
        return 1

    source = loader.get_source()
    if source is None:
        logger.error(
            "%s: could not load source for default settings module", prog)
        return 1

    print(source)
    return 0


if __name__ == '__main__':
    sys.exit(main())
