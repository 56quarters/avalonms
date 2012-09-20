.. Avalon Music Server documentation master file, created by
   sphinx-quickstart on Tue May 22 21:54:05 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. NOTE: Copied from README.rst, keep in sync.
   Copied because github won't execute include directives so
   having the README.rst just include some common text file
   isn't an option.

Avalon Music Server
===================

The Avalon Music Server is a BSD licensed server that scans meta data
from a music collection and provides a JSON interface to it over HTTP.

The server is able to read meta data from ogg, flac, and mp3 files. Clients
can then query the server to pull information about songs, albums, artists, 
and genres in the collection.


Contents
========
.. toctree::
   :maxdepth: 1
   
   requirements
   installation
   usage
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

