# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#

from __future__ import print_function, unicode_literals

from fabric.api import hide, local, task


@task(name='released')
def build_released():
    """Build a wheel from a released version on PyPI."""
    with hide('stdout'):
        local("pip wheel --requirement requirements-prod.txt")
        local("pip wheel avalonms")


@task(name='local')
def build_local():
    """Build a wheel from the local checkout."""
    with hide('stdout'):
        local(
            "pip wheel "
            "--requirement requirements.txt "
            "--requirement requirements-prod.txt")
        local("pip wheel --no-deps .")
