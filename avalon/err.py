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


"""Errors messages (as callables) used by the Avalon Music Server."""


__all__ = [
    'ERROR_DUPLICATE_FIELD_VALUE',
    'ERROR_INVALID_FIELD',
    'ERROR_INVALID_FIELD_VALUE',
    'ERROR_NEGATIVE_FIELD_VALUE',
    'ERROR_SERVER_NOT_READY'
    ]


class _ErrorMessage(object):

    """Callable to interpolate string placeholders with values."""

    def __init__(self, tpt):
        """Set the template for this error message."""
        self.tpt = tpt

    def __call__(self, *args, **kwargs):
        """Apply the positional args to the template string."""
        return self.tpt % args


ERROR_DUPLICATE_FIELD_VALUE = _ErrorMessage("Dupliate value for field [%s]")
ERROR_INVALID_FIELD         = _ErrorMessage("Invalid field [%s]")
ERROR_INVALID_FIELD_VALUE   = _ErrorMessage("Invalid value for field [%s]")
ERROR_NEGATIVE_FIELD_VALUE  = _ErrorMessage("Value for field [%s] must be non-negative")
ERROR_SERVER_NOT_READY      = _ErrorMessage("Server is not ready or unable to serve requests")
