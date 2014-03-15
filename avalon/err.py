# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2014 TSH Labs <projects@tshlabs.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
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


ERROR_DUPLICATE_FIELD_VALUE = _ErrorMessage("Duplicate value for field [%s]")
ERROR_INVALID_FIELD = _ErrorMessage("Invalid field [%s]")
ERROR_INVALID_FIELD_VALUE = _ErrorMessage("Invalid value for field [%s]")
ERROR_NEGATIVE_FIELD_VALUE = _ErrorMessage("Value for field [%s] must be non-negative")
ERROR_SERVER_NOT_READY = _ErrorMessage("Server is not ready or unable to serve requests")
