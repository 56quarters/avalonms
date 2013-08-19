Avalon Music Server
===================

The Avalon Music Server is an HTTP server that scans metadata from a music
collection and exposes it as a JSON web service.

The server is able to read metadata from ogg, flac, and mp3 files. Clients
can then query the server for information about songs, albums, artists,
and genres in the collection.


Using it is as simple as

  avalonmsd ~/Music

The server can also be run as a well-behaved Unix daemon

  avalonmsd --daemon --error-log /tmp/error.log --access-log /tmp/access.log ~/Music


Features include:

* Support for Mp3, Vorbis (Ogg), or Flac audio files
* Simple, clean JSON interface
* Tunable concurrency support
* Unicode output support
* Running as a daemon (including dropping super user permissions)
* IPv6 support

The latest documentation is available at https://avalonms.readthedocs.org/en/latest/

The source is available at https://github.com/tshlabs/avalonms

The ChangeLog is available at https://raw.github.com/tshlabs/avalonms/master/ChangeLog

.. image:: https://travis-ci.org/tshlabs/avalonms.png?branch=master
    :target: https://travis-ci.org/tshlabs/avalonms
