# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Scan the music collection and insert meta data into the database."""

from __future__ import absolute_import, unicode_literals

import argparse
import logging
import sys

import os.path
import avalon
import avalon.app.factory
import avalon.app.scan
import avalon.compat
import avalon.exc
import avalon.log
from avalon.app.bootstrap import build_config, CONFIG_ENV_VAR
from avalon.cli import install_sigint_handler


def get_opts(prog):
    parser = argparse.ArgumentParser(
        prog=prog,
        description=__doc__)

    parser.add_argument(
        'collection',
        help='Path to the root of your music collection')

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=avalon.__version__,
        help='Show the version of the Avalon Music Server and exit')

    parser.add_argument(
        '-d',
        '--database-url',
        metavar='URL',
        help='Database URL connection string for the database to '
             'write music collection meta data to. If not specified '
             'the value from the default configuration file and '
             'configuration file override will be used. The URL must '
             'be one supported by SQLAlchemy. See documentation '
             'here: http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls')

    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Be less verbose, only emit ERROR level messages to the '
             'console')

    return parser.parse_args()


def main():
    install_sigint_handler()
    prog = os.path.basename(sys.argv[0])
    args = get_opts(prog)
    config = build_config(env_var=CONFIG_ENV_VAR)

    if args.database_url:
        config['DATABASE_URL'] = avalon.cli.input_to_text(args.database_url)

    if args.quiet:
        config['LOG_LEVEL'] = logging.ERROR

    logger = avalon.log.get_error_log()
    avalon.app.factory.configure_logger(logger, config)

    try:
        database = avalon.app.factory.new_db_engine(config)
        database.connect()
    except avalon.exc.DatabaseError as e:
        logger.error("%s: %s", prog, e)
        return 1

    dao = avalon.app.factory.new_dao(database)
    id_cache = avalon.app.factory.new_id_cache(dao)
    scanner = avalon.app.scan.AvalonCollectionScanner(database, id_cache)
    collection = avalon.cli.input_to_text(args.collection)

    try:
        scanner.scan_path(collection)
    except avalon.exc.AvalonError as e:
        logger.error(
            "%s: Scanning of music collection at %s failed: %s",
            prog, args.collection, e)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
