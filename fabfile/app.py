# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#

from __future__ import unicode_literals
from fabric.api import sudo, task


@task
def start():
    """Start the Avalon app under supervisor."""
    sudo("supervisorctl start avalon")


@task
def stop():
    """Stop the Avalon app under supervisor."""
    sudo("supervisorctl stop avalon")


@task
def restart():
    """Restart the Avalon app under supervisor."""
    sudo("supervisorctl restart avalon")