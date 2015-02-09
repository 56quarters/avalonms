# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright 2012-2015 TSH Labs <projects@tshlabs.org>
#
# Available under the MIT license. See LICENSE for details.
#

"""Compatibility methods for running under Python 2 and Python 3."""

from __future__ import absolute_import, unicode_literals
import avalon
from avalon.packages import six


def to_text(value, encoding=None):
    """Convert the given text or binary type to text using
    the given encoding or the default encoding for the Avalon
    Music Server (UTF-8).

    :data:`None` values will be converted to an empty text string,
    text values will be left alone, and binary values will be
    converted using the specified or default encoding. All other
    types will result in a :class:`TypeError` being raised

    :param value: Possible text or binary value
    :param basestring encoding: Optional encoding to use for converting
        from bytes to a text type
    :return: The value converted to text
    :raises TypeError: If the type of the value isn't supported.
    """
    encoding = avalon.DEFAULT_ENCODING if encoding is None else encoding

    if value is None:
        return six.text_type()
    if isinstance(value, six.text_type):
        return value
    if isinstance(value, six.binary_type):
        return value.decode(encoding)
    raise TypeError("Cannot convert type {0} to text".format(type(value)))


def to_uuid_input(value):
    """Convert a text string (``unicode`` in Python 2, ``str`` in
    Python 3) to the appropriate form to be used by the :mod:`uuid`
    factory methods.

    If we are running under Python 2, convert the unicode object to
    UTF-8 encoded bytes. If we are running under Python 3 return the
    unicode object unchanged.

    :param unicode value: Text (unicode) string
    :return: The text string unchanged or converted to UTF-8 bytes
    :raises TypeError: If the type of the value isn't supported
    """
    if six.PY2 and isinstance(value, six.text_type):
        # uuid.uuid3() and uuid.uuid5() expect bytes in Python 2
        # as input and all the values we have are unicode objects,
        # convert them using our default character set (UTF-8).
        return value.encode(avalon.DEFAULT_ENCODING)
    if six.PY3 and isinstance(value, six.text_type):
        # Our values are all unicode objects which is what the uuid
        # functions expect in Python 3 so just return it verbatim.
        return value
    raise TypeError("Cannot convert type {0} to UUID input".format(type(value)))
