# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 TSH Labs <projects@tshlabs.org>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


"""Errors messages (as callables) used by the Avalon Music Server."""


__all__ = [
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


ERROR_INVALID_FIELD        = _ErrorMessage("Invalid field [%s]")
ERROR_INVALID_FIELD_VALUE  = _ErrorMessage("Invalid value for field [%s]")
ERROR_NEGATIVE_FIELD_VALUE = _ErrorMessage("Value for field [%s] must be non-negative")
ERROR_SERVER_NOT_READY     = _ErrorMessage("Server is not ready or unable to serve requests")
