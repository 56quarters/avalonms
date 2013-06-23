Genres endpoint
~~~~~~~~~~~~~~~

The ``genres`` endpoint returns data for all the different genres that songs in
the music collection belong to.


Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

============= ============= ============= ============= ===============================================================
Name          Required?     Type          Mutiple?      Description
============= ============= ============= ============= ===============================================================
``query``     No            ``string``    No            Select only genres whose name contains ``query``. The match is
                                                        not case sensitive and unicode characters will be normalized if
                                                        possible before being compared (in the ``query`` and fields
                                                        being compared). The ``query`` is compared using prefix
                                                        matching against each portion of the genre (delimitted by
                                                        whitespace).
============= ============= ============= ============= ===============================================================

Other Parameters
^^^^^^^^^^^^^^^^

.. include:: order_limit.rst


Example request
^^^^^^^^^^^^^^^

* http://api.tshlabs.org/avalon/genres

* http://api.tshlabs.org/avalon/genres?query=rock

* http://api.tshlabs.org/avalon/genres?order=name

* http://api.tshlabs.org/avalon/genres?order=name&limit=10


Possible error responses
^^^^^^^^^^^^^^^^^^^^^^^^

* ``INVALID_PARAMETER_ERROR`` will be returned if an invalid value for a query string parameter was passed. The HTTP
  status code will be ``400`` in this case.


* ``SERVER_NOT_READY_ERROR`` will be returned if a request was made before the server finished starting. The HTTP
  status code will be ``503`` in this case.


Success output format
^^^^^^^^^^^^^^^^^^^^^

  ::

    {
      "is_error": false,
      "error_name": "",
      "error_msg": "",
      "result_count": 2,
      "results": [
        {
          "id": "8794d7b7-fff3-50bb-b1f1-438659e05fe5",
          "name": "Punk"      
        },
        {
          "id": "62d4db4c-160c-52e4-8c47-bf2e7b412ca2",
          "name": "Ska"
        }
      ]
    }


Error output format
^^^^^^^^^^^^^^^^^^^

  ::

    {
      "is_error": true,
      "error_name": "SERVER_NOT_READY_ERROR",
      "error_msg": "Server has not finished start up",
      "result_count": 0,
      "results": []
    }



