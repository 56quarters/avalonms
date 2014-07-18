Heartbeat Endpoint
~~~~~~~~~~~~~~~~~~

The ``heartbeat`` endpoint returns the plain text string ``OKOKOK`` if the server has
completed starting and loading collection data. Requests to the heartbeat will hang until
the server has completed starting. The heartbeat does NOT indicate if the server is healthy
and serving requests correctly, only that it has completed start up. The idea being, that
this is used durning a rolling deploy process where there are multiple nodes behind a load
balancer.


Path and method
^^^^^^^^^^^^^^^

``GET /avalon/heartbeat``


Parameters
^^^^^^^^^^

* The ``heartbeat`` endpoint doesn't support any parameters.


Possible error responses
^^^^^^^^^^^^^^^^^^^^^^^^

* The ``heartbeat`` endpoint doesn't return a JSON response object.


Success output format
^^^^^^^^^^^^^^^^^^^^^

  ::

    OKOKOK


Error output format
^^^^^^^^^^^^^^^^^^^

  ::

    NONONO


Example request
^^^^^^^^^^^^^^^

* http://api.tshlabs.org/avalon/heartbeat

