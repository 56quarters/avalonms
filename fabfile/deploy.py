# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#

from __future__ import print_function, unicode_literals

from datetime import datetime
import uuid

from os.path import basename, join
from fabric.api import (
    env,
    execute,
    hide,
    put,
    puts,
    run,
    sudo,
    task,
    warn,
    warn_only)


@task(default=True)
def deploy():
    """Upload and install artifacts and mark a new release as 'current'."""
    execute(setup)
    execute(upload)
    execute(install)
    execute(cleanup)
    execute(permissions)


@task
def current():
    """Get the release ID of the install pointed to by 'current'."""
    puts(get_current_version())


@task
def setup():
    """Set up the required directories for an install."""
    for path in (
            env.remote_build_path,
            env.remote_deploy_base,
            env.remote_deploy_releases):
        run('mkdir -p %s' % path)


@task
def upload():
    """Upload the build artifacts to the server."""
    put('wheelhouse', env.remote_build_path)


@task
def install():
    """Install into a virtualenv and mark it 'current'."""
    with hide('stdout'):
        release_id = setup_virtual_env()
        patch_virtual_env(release_id)
        install_from_wheels(release_id)
        set_version_as_current(release_id)


@task
def cleanup(keep=5):
    """Remove build artifacts and all but a few of the most recent releases."""
    releases = get_releases()
    # Get a list of all releases that aren't the N newest ones and
    # also aren't the release being pointed to by the 'current'
    # symlink
    current_version = get_current_version()
    to_delete = [version for version in releases[keep:] if version != current_version]

    for release in to_delete:
        run("rm -rf %s/%s" % (env.remote_deploy_releases, release))

    run("rm -rf %s" % env.remote_build_path)


@task
def rollback():
    """Rollback to the previous release."""
    releases = get_releases()
    if not releases:
        warn("No available releases, cannot rollback")
        return

    current_ver = get_current_version()
    if not current_ver:
        warn("No current version available, cannot rollback")
        return

    try:
        current_index = releases.index(current_ver)
    except ValueError:
        warn("Could not determine current version, cannot rollback")
        return

    try:
        previous_version = releases[current_index + 1]
    except IndexError:
        warn("No previous version before current, cannot rollback")
        return

    set_version_as_current(previous_version)


@task
def permissions():
    """Fix the permissions and owner of the deploy directory."""
    sudo('chown -R %s %s' % (env.remote_deploy_owner, env.remote_deploy_base))
    sudo('chmod -R %s %s' % (env.remote_deploy_perms, env.remote_deploy_base))


def get_releases():
    """Get the current releases, newest first."""
    return run("ls -1r %s" % env.remote_deploy_releases).split()


def get_current_version():
    """Get the release ID of the release that is 'current' or None."""
    with warn_only():
        target = run('readlink %s' % env.remote_deploy_current)

    if target.failed:
        return None
    return basename(target.strip())


def setup_virtual_env():
    """Generate a release ID and create a new virtualenv."""
    release_id = datetime.utcnow().strftime(env.release_id_fmt)
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


def set_version_as_current(version):
    """Update the 'current' symlink to point at the given release ID."""
    tmp_path = join(env.remote_deploy_base, str(uuid.uuid4()))

    target = join(env.remote_deploy_releases, version)
    final_path = env.remote_deploy_current

    # First create a link with a random name to point to the
    # newly created release, then rename it to 'current' such
    # that the symlink is updated atomically [1].
    # [1] - http://rcrowley.org/2010/01/06/things-unix-can-do-atomically
    run("ln -s %s %s" % (target, tmp_path))
    run("mv -T %s %s" % (tmp_path, final_path))
