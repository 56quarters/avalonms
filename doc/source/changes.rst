Change Log
==========

0.5.1 - 2015-04-04
------------------
* Packaging fixes (use ``twine`` for uploads to PyPI, stop using the setup.py
  ``register`` command).
* Add documentation of the steps for performing a release (:doc:`maintainers`).
* Split usage documentation between :doc:`the CLI </cli>` and
  :doc:`the server </server>`.

0.5.0 - 2015-01-04
------------------
* Add optional support for recording method execution times to Statsd. Enabling
  timing requires installing the `pystatsd <https://github.com/jsocol/pystatsd>`_
  client and setting configuration values to point to your statsd instance.
* Remove ``supervisor.config`` and ``supervisor.user`` tasks from bundled Fabric
  script and move ``supervisor.restart`` to ``deploy.supervisor`` (along with
  having Supervisor gracefully reload instead of restart).

0.4.0 - 2014-11-24
------------------
* Change to Mutagen for reading audio tags now that it supports Python 3.
* Support for Python 3.3 and 3.4.
* Reduce memory usage during bootstrap by reading metadata in batches.
* Reduce memory usage during collection scanning by inserting tracks in batches.

0.3.1 - 2014-10-12
------------------
* Include installation of a Sentry client in Fabric deploy task
* Use Py.test and Tox for running tests.
* Added a "Quick Start" section to the installation docs.
* Use `Tunic <http://tunic.rtfd.org>`_ library in Fabric deploy scripts.

0.3.0 - 2014-08-17
------------------
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

0.2.25 - 2014-03-19
-------------------
* License change from Apache 2 to MIT
* Unit test coverage improvements
* Removed server status page
* Remove dependency on the daemon library
* Various code quality improvements

0.2.24 - 2013-08-19
-------------------
* Fix bug in setup.py that prevented installation in Python 2.6
* Unit test coverage improvements
* Testing infrastructure improvements (Tox, Travis CI)
* Documentation for development environment setup
* Various typo and documentation updates

0.2.23 - 2013-06-17
-------------------
* Changes to the names of API errors and setting HTTP statuses correctly
* Sample deploy and init scripts for the Avalon Music Server
* Testability improvements for the avalon.cache layer
* Documentation improvements

0.2.22 - 2013-05-20
-------------------
* Handle database errors during rescan better
* Various code quality improvements
* Improved test coverage

0.2.21 - 2013-02-18
-------------------
* Bug fixes for the /heartbeat endpoint
* JSON responses now set the correct encoding (UTF-8)
* Improved test coverage

0.2.20 - 2013-02-02
-------------------
* Updates to status page to use Twitter Bootstrap
* Packaging fixes

0.2.15 - 2013-01-30
-------------------
* Changed to Apache license 2.0 instead of FreeBSD license
* Updated copyright for 2013

0.2.14 - 2013-01-21
-------------------
* Text searching using a Trie for faster matching
* Documentation improvements

0.2.13 - 2013-01-10
-------------------
* Unicode code folding for better search results
* Beginnings of a test suite for the supporting library
* Documentation links to reference server installation

0.2.12 - 2012-12-28
-------------------
* Text searching functionality via 'query' param for
  albums, artists, genres, and songs endpoints
* Documentation updates for installation

0.2.11 - 2012-12-23
-------------------
* Refactor avalon.scan into avalon.tags package
* Switch to use Mutagen by default instead of TagPy
* Allow avalon.tags package to fall back to TagPy if
  Mutagen isn't installed

0.2.10 - 2012-12-17
-------------------
* Fix build dependencies and remove setuptools/distribute requirement

0.2.9 - 2012-12-17
------------------
* Minor documentation updates

0.2.8 - 2012-12-15
------------------
* Updates to the build process

0.2.5 - 2012-12-13
------------------
* Packaging fixes

0.2.0 - 2012-12-13
------------------
* **Breaking change**: Use of UUIDs for stable IDs for albums, artists, genres, and songs
* Documentation improvements
* Ordering, limit, and offset parameter support

0.1.0 - 2012-05-20
------------------
* Initial release
