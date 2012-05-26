API
---

The Avalon Music Server handles requests on the specified interface and
port at the path ``/avalon``.

Meta data endpoints return information about a music collection in JSON
format based on path and/or query string parameters.

* ``/avalon/songs``

* ``/avalon/albums``

* ``/avalon/artists``

* ``/avalon/genres``

Informational endpoints return information about the current status of
the server in text/html format.

* ``/avalon/``

* ``/avalon/heartbeat``


.. include:: api/status.rst

.. include:: api/heartbeat.rst

.. include:: api/songs.rst

.. include:: api/albums.rst

.. include:: api/artists.rst

.. include:: api/genres.rst

