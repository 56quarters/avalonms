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


def test_partition():
    input_list = ['one', 'two', 'three', 'four', 'five']
    generator = avalon.util.partition(input_list, 2)
    part_1 = next(generator)
    part_2 = next(generator)
    part_3 = next(generator)

    assert 2 == len(part_1)
    assert 2 == len(part_2)
    assert 1 == len(part_3)

    assert 'one' in part_1
    assert 'two' in part_1
    assert 'three' in part_2
    assert 'four' in part_2
    assert 'five' in part_3

