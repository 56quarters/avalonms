Albums endpoint
~~~~~~~~~~~~~~~

The ``albums`` endpoint returns data for all the different albums that songs
in the music collection belong to.


Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

============= ============= ============= ============= ===============================================================
Name          Required?     Type          Mutiple?      Description
============= ============= ============= ============= ===============================================================
``query``     No            ``string``    No            Select only albums whose name contains ``query``. The match is
                                                        not case sensitive and unicode characters will be normalized if
                                                        possible before being compared (in the ``query`` and fields
                                                        being compared). The ``query`` is compared using prefix
                                                        matching against each portion of the album (delimitted by
                                                        whitespace).
============= ============= ============= ============= ===============================================================

Other Parameters
^^^^^^^^^^^^^^^^

.. include:: order_limit.rst


Example request
^^^^^^^^^^^^^^^

* http://api.tshlabs.org/avalon/albums

* http://api.tshlabs.org/avalon/albums?query=live

* http://api.tshlabs.org/avalon/albums?order=name&direction=asc

* http://api.tshlabs.org/avalon/albums?order=name&direction=desc&limit=5


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
          "id": "2d24515c-a459-552a-b022-e85d1621425a",
          "name": "Dookie"      
        },
        {
          "id": "b3c204e4-445d-5812-9366-28de6770c4e1",
          "name": "Insomniac"
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



