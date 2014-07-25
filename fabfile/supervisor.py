# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#

from __future__ import unicode_literals
import uuid

from os.path import join
from fabric.api import env, run, sudo, task, quiet


# NOTE: Tasks in this module typically require sudo on the remote host


@task
def user():
    """Add an Avalon user and group if it doesn't exist."""
    with quiet():
        usr_res = run('id %s' % env.app_user)

    if usr_res.failed:
        sudo('useradd --shell %s --home %s --user-group %s' % (
            '/bin/false', env.remote_deploy_base, env.app_user))


@task
def config():
    """Ensure that there's a link to the Avalon supervisord config."""
    tmp_path = join(env.remote_supervisor_config, str(uuid.uuid4()))

    target = join(env.remote_deploy_current_share, "avalon-supervisor-gunicorn.conf")
    final_path = join(env.remote_supervisor_config, "avalon-supervisor-gunicorn.conf")

    # First create a link with a random name to point to the 'current'
    # Avalon Supervisor config, then rename it to the final file name
    # such that the symlink is updated atomically [1].
    # [1] - http://rcrowley.org/2010/01/06/things-unix-can-do-atomically
    sudo("ln -s %s %s" % (target, tmp_path))
    sudo("mv -T %s %s" % (tmp_path, final_path))


@task
def restart():
    """Restart supervisord to pick up new config files."""
    # For some reason the 'restart' action always exits with status
    # '1' and I can't figure out why. So, we work around it by just
    # starting and stopping.
    sudo("service supervisor stop")
    sudo("service supervisor start")