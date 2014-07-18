# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals
import errno

import avalon.util


def test_is_perm_error_yes():
    """Test that we can identify a permission error."""
    e = IOError(errno.EACCES, "Busted!")
    assert avalon.util.is_perm_error(e)


def test_is_perm_error_no():
    """Test that we can identify something that isn't a permission
    error.
    """
    e = IOError(errno.ENOTDIR, "Busted!")
    assert False is avalon.util.is_perm_error(e)


def test_is_perm_error_not_io_error():
    """Test that non-IOErrors are handled correctly."""
    e = Exception("Rut roh")
    assert False is avalon.util.is_perm_error(e)
