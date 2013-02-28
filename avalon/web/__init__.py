# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2013 TSH Labs <projects@tshlabs.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""Avalon web endpoint handler package."""


import pkgutil
import os


__all__ = [
    'DATA_DIR',
    'CONF_FILE'
    ]


_loader = pkgutil.get_loader('avalon.web')
_package_base = os.path.dirname(_loader.get_filename())


# Constants referenced by the INI config file
DATA_DIR = os.path.join(_package_base, 'data')
CONF_FILE = os.path.join(DATA_DIR, 'config.ini')


del _loader, _package_base

