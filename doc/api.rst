API
---

The Avalon Music Server handles requests on the specified interface and
port at the path ``/avalon``.

Meta data endpoints return information about a music collection in JSON
format based on path and/or query string parameters. Endpoints will return
data as JSON and set HTTP response code ``200`` for successful requests.
Errors will still return JSON results but will set a non-``200`` response
code such as ``400``, ``500``, ``501``, or ``503``.

* ``/avalon/songs``

* ``/avalon/albums``

* ``/avalon/artists``

* ``/avalon/genres``

Informational endpoints return information about the current status of
the server in text/html format.

* ``/avalon/``

* ``/avalon/heartbeat``


Endpoints
=========

.. toctree::
   :maxdepth: 1
   
   api/status
   api/heartbeat
   api/songs
   api/albums       
   api/artists
   api/genres

