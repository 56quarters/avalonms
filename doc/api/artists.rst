Artists endpoint
~~~~~~~~~~~~~~~~

The ``artists`` endpoint returns data for all the different artists that songs
in the music collection are performed by.


Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

============= ============= ============= ============= ===============================================================
Name          Required?     Type          Mutiple?      Description
============= ============= ============= ============= ===============================================================
``query``     No            ``string``    No            Select only artists whose name contains ``query``. The match is
                                                        not case sensitive and unicode characters will be normalized if
                                                        possible before being compared (in the ``query`` and fields
                                                        being compared). The ``query`` is compared using prefix
                                                        matching against each portion of the artist (delimitted by
                                                        whitespace).
============= ============= ============= ============= ===============================================================

Other Parameters
^^^^^^^^^^^^^^^^^^^^

.. include:: order_limit.rst


Example request
^^^^^^^^^^^^^^^

* http://api.tshlabs.org/avalon/artists

* http://api.tshlabs.org/avalon/artists?query=who

* http://api.tshlabs.org/avalon/artists?order=id

* http://api.tshlabs.org/avalon/artists?order=name&limit=10&offset=20


Possible error responses
^^^^^^^^^^^^^^^^^^^^^^^^

* ``InvalidParameterError`` will be returned if an invalid value for a query string parameter was passed. The HTTP
  status code will be ``200`` in this case.

* ``ServerNotReadyError`` will be returned if a request was made before the server finished starting. The HTTP
  status code will be ``200`` in this case.


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
          "id": 123,
          "name": "Green Day"      
        },
        {
          "id": 456,
          "name": "Bad Religion"
        }
      ]
    }


Error output format
^^^^^^^^^^^^^^^^^^^

  ::

    {
      "is_error": true,
      "error_name": "ServerNotReadyError",
      "error_msg": "Server has not finished start up",
      "result_count": 0,
      "results": []
    }


