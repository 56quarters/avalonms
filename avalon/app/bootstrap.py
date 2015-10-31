# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
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
import avalon.log
import avalon.metrics
import avalon.web.response
import avalon.app.factory
import avalon.tags.insert
import avalon.util

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

    # Register a Sentry client for log messages at ERROR or higher
    # if the client is installed and configured, otherwise this has
    # no effect.
    avalon.app.factory.configure_sentry_logger(log, app.config)

    # Get a StatsClient instance if installed and update the singleton
    # metrics bridge instance with it. This allows decorators executed
    # before the client is bootstrapped to talk to it once it's ready.
    stats_client = avalon.app.factory.new_stats_client(log, app.config)
    avalon.metrics.bridge.client = stats_client

    log.info("Connecting to database")
    database = avalon.app.factory.new_db_engine(app.config)
    database.connect()

    dao = avalon.app.factory.new_dao(database)
    id_cache = avalon.app.factory.new_id_cache(dao)

    log.info("Building in-memory stores")
    controller = avalon.app.factory.new_controller(dao, id_cache)
    controller.reload()

    app.json_decoder = avalon.web.response.AvalonJsonDecoder
    app.json_encoder = avalon.web.response.AvalonJsonEncoder

    request_path = app.config['REQUEST_PATH']
    path_resolver = _EndpointPathResolver(request_path)

    app.add_url_rule(path_resolver('version'), view_func=controller.get_version)
    app.add_url_rule(path_resolver('heartbeat'), view_func=controller.get_heartbeat)
    app.add_url_rule(path_resolver('albums'), view_func=controller.get_albums)
    app.add_url_rule(path_resolver('artists'), view_func=controller.get_artists)
    app.add_url_rule(path_resolver('genres'), view_func=controller.get_genres)
    app.add_url_rule(path_resolver('songs'), view_func=controller.get_songs)

    # Catch-all for any unexpected errors that ensures we still render
    # a JSON payload in the same format the client is expecting while
    # also logging the exception.
    app.register_error_handler(Exception, controller.handle_unknown_error)

    log.info(
        "Avalon Music Server %s running with request path %s as %s:%s "
        "using %s MB memory", avalon.__version__, request_path,
        avalon.util.get_current_uname(), avalon.util.get_current_gname(),
        avalon.util.get_mem_usage())

    return app


class _EndpointPathResolver(object):
    """Logic for combining a user supplied 'REQUEST_PATH' setting and
    each of the various endpoints supported by the Avalon Music Server
    and figuring out the path they should live at.
    """
    _logger = avalon.log.get_error_log()

    def __init__(self, base):
        """Set the user supplied request base.

        :param unicode base: User supplied request base. By default this
            is '/avalon' but may be anything (including just a '/') as long
            as it starts with a '/'.
        """
        self._base = base

    def __call__(self, endpoint):
        """Determine the appropriate path for the given endpoint based the
        user supplied REQUEST_PATH setting, ensuring that the user has given
        us a reasonable value.
        """
        assert not endpoint.startswith('/'), "Endpoint should not start with '/'"

        base = self._base
        if not base.startswith('/'):
            raise ValueError("The REQUEST_PATH setting must start with a '/'")
        if base != '/' and base.endswith('/'):
            raise ValueError("The REQUEST_PATH setting must not end with a '/'")

        if base == '/':
            path = base + endpoint
        else:
            path = base + '/' + endpoint

        self._logger.debug("Resolved path %s for %s endpoint", path, endpoint)
        return path


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
