Albums endpoint
~~~~~~~~~~~~~~~

The ``albums`` endpoint returns data for all the different albums that songs
in the music collection belong to.


Path and method
^^^^^^^^^^^^^^^

``GET /avalon/albums``


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

================= ========================================= ============= ===================================
Code              Message key                               HTTP code     Description
================= ========================================= ============= ===================================
100               avalon.service.error.invalid_input_name   400           An error that indicates that the
                                                                          name of a field specified is not a
                                                                          valid field.
----------------- ----------------------------------------- ------------- -----------------------------------
101               avalon.service.error.invalid_input_type   400           An error that indicates the type of
                                                                          a parameter is not valid for that
                                                                          particular parameter.
----------------- ----------------------------------------- ------------- -----------------------------------
102               avalon.service.error.invalid_input_value  400           An error that indicates the value
                                                                          of a parameter is not valid for
                                                                          that particular parameter.
================= ========================================= ============= ===================================

Success output format
^^^^^^^^^^^^^^^^^^^^^

  ::

    {
      "warnings": [],
      "success": [
        {
          "name": "The Living End",
          "id": "9f311017-f1a8-598c-b842-fe873a4d198f"
        },
        {
          "name": "End of the Century",
          "id": "5209928c-4527-5fa5-a1de-affc4d9f6c11"
        },
        {
          "name": "Endgame",
          "id": "491672c5-adbe-5414-a4b5-cb6f3af03a6a"
        }
      ],
      "errors": []
    }



Error output format
^^^^^^^^^^^^^^^^^^^

  ::

    {
      "warnings": [],
      "success": null,
      "errors": [
        {
          "payload": {
            "value": -1,
            "field": "limit"
          },
          "message_key": "avalon.service.error.invalid_input_value",
          "message": "The value of limit may not be negative",
          "code": 102
        }
      ]
    }
