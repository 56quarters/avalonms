# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Functionality for assembling and configuring the Avalon Music Server as
a WSGI application."""

from __future__ import print_function, unicode_literals

import pkgutil

import os
from flask import Flask, Config
import avalon
import avalon.exc
import avalon.ids
import avalon.web.response
import avalon.app.factory
import avalon.tags.insert
import avalon.util


__all__ = [
    'CONFIG_ENV_VAR',
    'bootstrap',
    'build_config'
]

CONFIG_ENV_VAR = 'AVALON_CONFIG'


def bootstrap(config_env=None):
    """Build, configure, and return a WSGI application using default
    settings from the avalon.settings module and optionally from the file
    referenced by the environmental variable.

    :return: Fully configured WSGI application
    :rtype: flask.Flask
    """
    # Note that we don't attempt to catch any potential exceptions during
    # bootstrap. Instead, we just let them bubble up and blow up whatever
    # context the application is being started in.

    app = _load_application(config_env)

    # Make sure to access the Flask application logger before trying to
    # configure it since Flask will remove all currently installed handlers
    # when initializing it. https://github.com/mitsuhiko/flask/issues/641
    log = app.logger
    avalon.app.factory.configure_logger(log, app.config)

    if config_env is not None:
        log.info(
            "Attempted to load config from var %s (%s)",
            config_env, os.getenv(config_env))

    log.info("Connecting to database...")
    database = avalon.app.factory.new_db_engine(app.config)
    database.connect()

    dao = avalon.app.factory.new_dao(database)
    id_cache = avalon.app.factory.new_id_cache(dao)

    log.info("Building in-memory stores...")
    controller = avalon.app.factory.new_controller(dao, id_cache)
    controller.reload()

    app.json_decoder = avalon.web.response.AvalonJsonDecoder
    app.json_encoder = avalon.web.response.AvalonJsonEncoder

    app.add_url_rule('/avalon/heartbeat', view_func=controller.heartbeat)
    app.add_url_rule('/avalon/version', view_func=controller.version)

    app.add_url_rule('/avalon/albums', view_func=controller.albums)
    app.add_url_rule('/avalon/artists', view_func=controller.artists)
    app.add_url_rule('/avalon/genres', view_func=controller.genres)
    app.add_url_rule('/avalon/songs', view_func=controller.songs)

    # Catch-all for any unexpected errors that ensures we still render
    # a JSON payload in the same format the client is expecting while
    # also logging the exception.
    app.register_error_handler(Exception, controller.handle_unknown_error)

    log.info(
        "Avalon Music Server %s running as %s:%s using %s MB memory",
        avalon.__version__, avalon.util.get_current_uname(),
        avalon.util.get_current_gname(), avalon.util.get_mem_usage())

    return app


def build_config(env_var=None):
    """Construct a new application configuration outside of a web app.

    The configuration will be loaded from the same sources as it would
    be when loaded from a Flask web app (defaults and site specific).

    This method should only be used when not loading a web app, such as
    when loading configuration for a CLI script. Web apps should use the
    :func:`bootstrap` method instead.

    :param str env_var: Name of the ENV var to load a site specific
        configuration file from. If the var is not specified or does
        not point to a valid configuration file it will be silently
        ignored.
    :return: Loaded configuration
    :rtype: Config
    """
    loader = pkgutil.find_loader('avalon')
    if loader is None:
        raise RuntimeError(
            "Could not find package loader for 'avalon' module")

    path = loader.get_filename()
    if path is None:
        raise RuntimeError(
            "Could not find full filename for 'avalon' module")

    conf = Config(path)
    _load_configuration(conf, env_var)
    return conf


def _load_configuration(conf, env_var):
    """Load default configuration settings into the given :class:`Config`
    instance and optionally try to load additional settings from the file
    pointed to by the given environmental variable.

    The environmental variable will be quietly ignored if it is not set or
    it does not point to a valid configuration file.
    """
    conf.from_object('avalon.settings')
    if env_var is None:
        return False

    # Ignore the var not being set since it's entirely reasonable
    # that a user hasn't configured it. No sense logging or printing
    # annoying things that aren't errors.
    return conf.from_envvar(env_var, silent=True)


def _load_application(config_env):
    """Construct and return a :class:`Flask` application loading default
    and installation specific configuration settings.
    """
    app = Flask('avalon')
    _load_configuration(app.config, config_env)
    return app
