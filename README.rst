Avalon Music Server
===================

The Avalon Music Server is a BSD licensed server that scans meta data
from a music collection and provides a JSON interface to it over HTTP.

The server is able to read meta data from ogg, flac, and mp3 files. Clients
can then query the server to pull information about songs, albums, artists, 
and genres in the collection.


Using it is as simple as

  avalonmsd ~/Music

The server can also be run as a well-behaved Unix daemon

  avalonmsd --daemon --error-log /tmp/error.log --access-log /tmp/access.log ~/Music


Features include:

* Support for mp3, ogg, or flac audio files (via TagPy)
* Simple, clean JSON interface
* Tunable concurrency support
* Unicode output support
* Running as a daemon (including dropping super user permissions)
* IPv6 support