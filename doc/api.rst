API
---

The Avalon Music Server handles requests on the specified interface and
port at the path ``/avalon``.

Informational endpoints return information about the current status of
the server in text/html format.

* ``/avalon/``

* ``/avalon/heartbeat``

Metadata endpoints return information about a music collection in JSON
format based on path and/or query string parameters. Endpoints will return
data as JSON for sucessful and error requests.

* ``/avalon/songs``

* ``/avalon/albums``

* ``/avalon/artists``

* ``/avalon/genres``


Endpoints
=========

Informational Endpoints
~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   api/status
   api/heartbeat

Metadata Endpoints
~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   api/songs
   api/albums       
   api/artists
   api/genres

