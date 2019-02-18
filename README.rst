Avalon Music Server
===================

.. image:: https://travis-ci.org/tshlabs/avalonms.png?branch=master
    :target: https://travis-ci.org/tshlabs/avalonms

.. image:: https://img.shields.io/pypi/v/avalonms.svg
    :target: https://pypi.python.org/pypi/avalonms

The Avalon Music Server is a Python WSGI application and several CLI scripts
that, together, scan metadata from a music collection, store it in a database,
and expose it as a JSON web service. It is available under the MIT license.

The Avalon Music Server is able to read metadata from ogg, flac, and mp3 files.
Clients can then query the server for information about songs, albums, artists,
and genres in the collection.

Features
--------

* Support for Mp3, Vorbis (Ogg), or Flac audio files
* Support for multiple database backends
* Simple JSON interface including fast prefix matching
* Unicode output support
* Python 2.7 -- 3.6

Installation
------------

To install it simply run

.. code-block:: bash

    $ pip install avalonms

Usage
-----

Then, to scan your music collection

.. code-block:: bash

    $ avalon-scan ~/Music

Then, start the application using a WSGI server like `Gunicorn <http://gunicorn.org/>`_

.. code-block:: bash

    $ gunicorn --preload avalon.app.wsgi:application

Documentation
-------------

The latest documentation is available at https://avalonms.readthedocs.io/en/latest/

Source
------

The source is available at https://github.com/tshlabs/avalonms

Download
--------

Python packages are available at https://pypi.python.org/pypi/avalonms

Changes
-------

The change log is available at https://avalonms.readthedocs.io/en/latest/changes.html
