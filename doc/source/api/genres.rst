Genres endpoint
~~~~~~~~~~~~~~~

The ``genres`` endpoint returns data for all the different genres that songs in
the music collection belong to.


Path and method
^^^^^^^^^^^^^^^

``GET /avalon/genres``

.. note::

    This path may be different depending on your ``REQUEST_PATH`` configuration setting.

Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

============= ============= ============= ============= ===============================================================
Name          Required?     Type          Mutiple?      Description
============= ============= ============= ============= ===============================================================
``query``     No            ``string``    No            Select only genres whose name contains ``query``. The match is
                                                        not case sensitive and unicode characters will be normalized if
                                                        possible before being compared (in the ``query`` and fields
                                                        being compared). The ``query`` is compared using prefix
                                                        matching against each portion of the genre (delimited by
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
          "name": "Hard Rock",
          "id": "ec93d3f1-3642-5beb-bb10-07f29bb18fc5"
        },
        {
          "name": "Punk Ska",
          "id": "3af7ba62-d87f-5258-af62-d7c5655ec567"
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
            "value": -10,
            "field": "offset"
          },
          "message_key": "avalon.service.error.invalid_input_value",
          "message": "The value of offset may not be negative",
          "code": 102
        }
      ]
    }
