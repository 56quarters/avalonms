# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#


"""Fabric commands for Avalon development tasks and deploys."""

from __future__ import unicode_literals
import os.path

from fabric.api import env, lcd, task, local

from . import app
from . import build
from . import deploy
from . import supervisor

env.remote_build_path = '/tmp/build'

env.remote_deploy_base = '/var/www/avalon'

env.remote_deploy_owner = 'root:dev'

env.remote_deploy_perms = 'u+rw,g+rw,o+r'

env.remote_deploy_releases = env.remote_deploy_base + '/releases'

env.remote_deploy_current = env.remote_deploy_base + '/current'

env.remote_deploy_current_share = env.remote_deploy_current + '/share/avalonms'

env.remote_supervisor_config = '/etc/supervisor/conf.d'

env.release_id_fmt = '%Y%m%d%H%M%S'

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


@task
def test():
    """Run the unit tests.

    Note this task is meant to be run from inside the virtualenv.
    """
    local('nosetests test')

