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
    ProjectSetup,
    VirtualEnvInstallation)


@task(default=True)
def deploy():
    """Upload and install artifacts and mark a new release as 'current'."""
    setup = ProjectSetup(env.remote_deploy_base)
    setup.setup_directories(use_sudo=False)

    run('mkdir -p %s' % env.remote_build_path)
    put('wheelhouse', env.remote_build_path)

    rm = ReleaseManager(env.remote_deploy_base)
    install(rm)

    rm.cleanup()
    run("rm -rf %s" % env.remote_build_path)

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


def install(release_manager):
    """Install into a virtualenv and mark it 'current'."""
    release_id = get_release_id()

    # We upgrade setuptools and pip as separate installs
    # since we run into issues when upgrading them both
    # at the same time.
    patches = [
        VirtualEnvInstallation(env.remote_deploy_base, ['setuptools']),
        VirtualEnvInstallation(env.remote_deploy_base, ['pip'])]

    project = VirtualEnvInstallation(
        env.remote_deploy_base,
        ['avalonms', 'gunicorn', 'raven'],
        [join(env.remote_build_path, 'wheelhouse')])

    with hide('stdout'):
        for patch in patches:
            patch.install(release_id, upgrade=True)
        project.install(release_id)
        release_manager.set_current_release(release_id)
