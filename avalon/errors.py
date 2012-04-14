# -*- coding: utf-8 -*-
#

class AvalonError(Exception):
    
    """
    """

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
    pass
