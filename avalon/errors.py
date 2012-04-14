# -*- coding: utf-8 -*-
#


"""Errors thrown by the Avalon music server."""


__all__ = [
    'AvalonError',
    'ConnectionError'
    ]


class AvalonError(Exception):
    
    """Base for all exceptions."""

    def __init__(self, msg, err=None):
        self.message = msg
        self.err = err

    def __str__(self):
        out = self.message
        if self.err is not None:
            out += ': ' + str(self.err)
        return out

    def trace(self):
        pass


class ConnectionError(AvalonError):

    """There was an error connecting to the database."""

