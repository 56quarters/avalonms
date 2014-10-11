Avalon Music Server
===================

The Avalon Music Server is a Python WSGI application and several CLI scripts
that, together, scan metadata from a music collection, store it in a database,
and expose it as a JSON web service. It is available under the MIT license.

The Avalon Music Server is able to read metadata from ogg, flac, and mp3 files.
Clients can then query the server for information about songs, albums, artists,
and genres in the collection.

Features include:

* Support for Mp3, Vorbis (Ogg), or Flac audio files
* Support for multiple database backends
* Simple JSON interface including fast prefix matching
* Unicode output support

To install it simply run

.. code-block:: bash

    $ pip install avalonms

Then, to scan your music collection

.. code-block:: bash

    $ avalon-scan ~/Music

Then, start the application using a WSGI server like `Gunicorn <http://gunicorn.org/>`_

.. code-block:: bash

    $ gunicorn --preload avalon.app.wsgi:application

The latest documentation is available at https://avalonms.readthedocs.org/en/latest/

The source is available at https://github.com/tshlabs/avalonms

The change log is available at https://avalonms.readthedocs.org/en/latest/changes.html

.. image:: https://travis-ci.org/tshlabs/avalonms.png?branch=master
    :target: https://travis-ci.org/tshlabs/avalonms
