# -*- coding: utf-8 -*-
#

import errno

import avalon.util


class TestFunctions(object):
    def test_is_perm_error_yes(self):
        """Test that we can identify a permission error."""
        e = IOError(errno.EACCES, "Busted!")
        assert avalon.util.is_perm_error(e)

    def test_is_perm_error_no(self):
        """Test that we can identify something that isn't a permission error."""
        e = IOError(errno.ENOTDIR, "Busted!")
        assert False is avalon.util.is_perm_error(e)

    def test_is_perm_error_not_io_error(self):
        """Test that non IOErrors are handle correctly."""
        e = Exception("Rut roh")
        assert False is avalon.util.is_perm_error(e)

