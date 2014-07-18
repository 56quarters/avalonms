# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#

from __future__ import unicode_literals
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
    """Remove existing Avalon supervisor config and link to the current config."""
    target = env.remote_deploy_current_share + "/avalon-supervisor-gunicorn.conf"
    final_path = env.remote_supervisor_config + "/avalon-supervisor-gunicorn.conf"

    sudo("rm -f %s" % final_path)
    sudo("ln -s %s %s" % (target, final_path))


@task
def restart():
    """Restart supervisord to pick up new config files."""
    # For some reason the 'restart' action always exits with status
    # '1' and I can't figure out why. So, we work around it by just
    # starting and stopping.
    sudo("service supervisor stop")
    sudo("service supervisor start")