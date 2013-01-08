Heartbeat Endpoint
~~~~~~~~~~~~~~~~~~

The ``heartbeat`` endpoint returns the plain text string ``OKOKOK`` if the server has
completed starting and loading collection data, the plain text string ``NONONO`` if it
has not.


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

