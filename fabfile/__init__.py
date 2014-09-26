# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Fabric commands for Avalon development tasks and deploys."""

import os.path

from fabric.api import env, lcd, task, local, warn_only
from tunic.api import get_releases_path, get_current_path

from . import app
from . import build
from . import deploy
from . import supervisor

env.remote_build_path = '/tmp/build'

env.remote_deploy_base = '/var/www/avalon'

env.remote_deploy_owner = 'root:dev'

env.remote_deploy_releases = get_releases_path(env.remote_deploy_base)

env.remote_deploy_current = get_current_path(env.remote_deploy_base)

env.remote_deploy_current_share = env.remote_deploy_current + '/share/avalonms'

env.remote_supervisor_config = '/etc/supervisor/conf.d'

env.app_user = 'avalon'


@task
def clean():
    """Remove build artifacts."""
    local('rm -rf wheelhouse')
    local('rm -rf dist')
    local('rm -rf build')

    with lcd('doc'):
        local('make clean')


@task
def docs():
    """Generate Sphinx documentation.

    Note this task is meant to be run from inside the virtualenv.
    """
    with lcd('doc'):
        local('make html')


@task
def lint():
    """Run pylint on the project using our configuration."""
    with warn_only():
        local('pylint --rcfile .pylintrc avalon')


@task
def push():
    """Push locally committed changes to remote repos."""
    local('git push origin')
    local('git push github')
    local('git push bitbucket')


@task
def push_tags():
    """Push local tags to remote repos."""
    local('git push --tags origin')
    local('git push --tags github')
    local('git push --tags bitbucket')


@task
def pypi():
    """Build a source package and upload to PyPI.

    Note this task is meant to be run from inside the virtualenv.
    """
    local('python setup.py register sdist upload')


@task
def setup(env_name='env'):
    """Install all local dependencies (potentially create a virtualenv).

    Note this task can be run from inside or outside the virtualenv.
    """
    if not os.path.exists(env_name):
        local('virtualenv %s' % env_name)
    local(
        "%s/bin/pip install "
        "--requirement requirements.txt "
        "--requirement requirements-dev.txt "
        "--requirement requirements-prod.txt" % env_name)
    local('%s/bin/pip install --no-deps -e .' % env_name)

