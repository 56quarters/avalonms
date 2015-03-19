.. Avalon Music Server documentation master file, created by
   sphinx-quickstart on Tue May 22 21:54:05 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. NOTE: Copied from README.rst, keep in sync.
   Copied because github won't execute include directives so
   having the README.rst just include some common text file
   isn't an option.

Avalon Music Server
-------------------

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
* Python 2.6 -- 3.4

To install it simply run

.. code-block:: bash

    $ pip install avalonms

Then, to scan your music collection

.. code-block:: bash

    $ avalon-scan ~/Music

Then, start the application using a WSGI server like `Gunicorn <http://gunicorn.org/>`_

.. code-block:: bash

    $ gunicorn --preload avalon.app.wsgi:application

The documentation linked below will go into more detail about how to configure and run
the Avalon Music Server in a production environment, how to interact with it using the
JSON web service, and how to set up an environment to develop it.

Contents
~~~~~~~~
.. toctree::
   :maxdepth: 2
   
   requirements
   installation
   usage
   api
   ids
   developers
   maintainers
   changes


Indices and tables
~~~~~~~~~~~~~~~~~~

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

