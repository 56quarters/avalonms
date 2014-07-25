Change Log for Avalon Music Server
==================================

2014-XX-XX - v0.3.0
-------------------
* **Breaking change**: Avalon Music Server is now a WSGI application and CLI
  scripts, not a stand-alone server.
* **Breaking change**: Response format changed to include ``errors``, ``warnings``,
  and ``success`` top-level elements. Response format of individual results
  remains unchanged.
* Change from using CherryPy web framework to Flask.
* Change from Mutagen to Mutagenx for potential Python 3 support.
* Change from Py.test to Nosetests.
* Lots of changes to potentially support Python 3.3 and 3.4 including use of
  the ``six`` library and testing those versions on Travis CI.
* Include reference Fabric deploy script.
* Include reference Gunicorn, uWSGI, and Supervisor configurations.

2014-03-19 - v0.2.25
--------------------
* License change from Apache 2 to MIT
* Unit test coverage improvements
* Removed server status page
* Remove dependency on the daemon library
* Various code quality improvements

2013-08-19 - v0.2.24
--------------------
* Fix bug in setup.py that prevented installation in Python 2.6
* Unit test coverage improvements
* Testing infrastructure improvements (Tox, Travis CI)
* Documentation for development environment setup
* Various typo and documentation updates

2013-06-17 - v0.2.23
--------------------
* Changes to the names of API errors and setting HTTP statuses correctly
* Sample deploy and init scripts for the Avalon Music Server
* Testability improvements for the avalon.cache layer
* Documentation improvements

2013-05-20 - v0.2.22
--------------------
* Handle database errors during rescan better
* Various code quality improvements
* Improved test coverage

2013-02-18 - v0.2.21
--------------------
* Bug fixes for the /heartbeat endpoint
* JSON responses now set the correct encoding (UTF-8)
* Improved test coverage

2013-02-02 - v0.2.16, v0.2.17, v0.2.18, v0.2.19, v0.2.20
--------------------------------------------------------
* Updates to status page to use Twitter Bootstrap
* Packaging fixes

2013-01-30 - v0.2.15
--------------------
* Changed to Apache license 2.0 instead of FreeBSD license
* Updated copyright for 2013

2013-01-21 - v0.2.14
--------------------
* Text searching using a Trie for faster matching
* Documentation improvements

2013-01-10 - v0.2.13
--------------------
* Unicode code folding for better search results
* Beginnings of a test suite for the supporting library
* Documentation links to reference server installation

2012-12-28 - v0.2.12
--------------------
* Text searching functionality via 'query' param for
  albums, artists, genres, and songs endpoints
* Documentation updates for installation

2012-12-23 - v0.2.11
--------------------
* Refactor avalon.scan into avalon.tags package
* Switch to use Mutagen by default instead of TagPy
* Allow avalon.tags package to fall back to TagPy if
  Mutagen isn't installed

2012-12-17 - v0.2.10
--------------------
* Fix build dependencies and remove setuptools/distribute requirement

2012-12-17 - v0.2.9
-------------------
* Minor documentation updates

2012-12-15 - v0.2.6, v0.2.7, v0.2.8
-----------------------------------
* Updates to the build process

2012-12-13 - v0.2.1, v0.2.2, v0.2.3, v0.2.4, v0.2.5
---------------------------------------------------
* Packaging fixes

2012-12-13 - v0.2.0
-------------------
* **Breaking change**: Use of UUIDs for stable IDs for albums, artists, genres, and songs
* Documentation improvements
* Ordering, limit, and offset parameter support

2012-05-20 - v0.1.0
-------------------
* Initial release
