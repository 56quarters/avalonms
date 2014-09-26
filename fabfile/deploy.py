# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#

from __future__ import print_function, unicode_literals

from os.path import join
from fabric.api import (
    env,
    hide,
    put,
    run,
    task,
    warn)
from tunic.api import (
    get_release_id,
    ReleaseManager,
    ProjectSetup)


@task(default=True)
def deploy():
    """Upload and install artifacts and mark a new release as 'current'."""
    setup = ProjectSetup(env.remote_deploy_base)
    setup.setup_directories(use_sudo=False)

    rm = ReleaseManager(env.remote_deploy_base)

    upload()
    install(rm)
    cleanup(rm)

    setup.set_permissions(env.remote_deploy_owner)


@task
def rollback():
    """Rollback to the previous release."""
    rm = ReleaseManager(env.remote_deploy_base)
    previous = rm.get_previous_release()

    if not previous:
        warn("No previous release, cannot rollback!")
        return

    rm.set_current_release(previous)


def upload():
    """Upload the build artifacts to the server."""
    run('mkdir %s' % env.remote_build_path)
    put('wheelhouse', env.remote_build_path)


def install(release_manager):
    """Install into a virtualenv and mark it 'current'."""

    with hide('stdout'):
        release_id = setup_virtual_env()
        patch_virtual_env(release_id)
        install_from_wheels(release_id)
        release_manager.set_current_release(release_id)


def cleanup(release_manager):
    """Remove build artifacts and all but a few of the most recent releases."""
    release_manager.cleanup()
    run("rm -rf %s" % env.remote_build_path)


def setup_virtual_env():
    """Generate a release ID and create a new virtualenv."""
    release_id = get_release_id()
    release_path = join(env.remote_deploy_releases, release_id)
    run('virtualenv %s' % release_path)
    return release_id


def patch_virtual_env(release_id):
    """Virtualenv on Debian Wheezy is too old."""
    virtual_env_path = join(env.remote_deploy_releases, release_id)
    install_tpt = "%s/bin/pip install --upgrade %s"
    for package in ('setuptools', 'pip'):
        run(install_tpt % (virtual_env_path, package))


def install_from_wheels(release_id):
    """Install the Avalon Music Server, Gunicorn, and a Sentry client into the virtualenv."""
    virtual_env_path = join(env.remote_deploy_releases, release_id)
    install_tpt = "%s/bin/pip install --no-index --find-links %s/wheelhouse %s"
    run(install_tpt % (virtual_env_path, env.remote_build_path, "raven"))
    run(install_tpt % (virtual_env_path, env.remote_build_path, "gunicorn"))
    run(install_tpt % (virtual_env_path, env.remote_build_path, "avalonms"))
