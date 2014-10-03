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
    task,
    warn)
from tunic.api import (
    get_release_id,
    LocalArtifactTransfer,
    ReleaseManager,
    ProjectSetup,
    VirtualEnvInstallation)


@task(default=True)
def deploy():
    """Upload and install artifacts and mark a new release as 'current'."""
    setup = ProjectSetup(env.remote_deploy_base)
    setup.setup_directories(use_sudo=False)

    transfer = LocalArtifactTransfer('wheelhouse', env.remote_build_path)
    with transfer:
        release_id = install()

    rm = ReleaseManager(env.remote_deploy_base)
    rm.set_current_release(release_id)
    rm.cleanup()

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


def install():
    """Install AvalonMS into a virtualenv."""
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
    return release_id
