Artists endpoint
~~~~~~~~~~~~~~~~

The ``artists`` endpoint returns data for all the different artists that songs
in the music collection are performed by.


Path and method
^^^^^^^^^^^^^^^

``GET /avalon/artists``

.. note::

    This path may be different depending on your ``REQUEST_PATH`` configuration setting.

Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

============= ============= ============= ============= ===============================================================
Name          Required?     Type          Mutiple?      Description
============= ============= ============= ============= ===============================================================
``query``     No            ``string``    No            Select only artists whose name contains ``query``. The match is
                                                        not case sensitive and unicode characters will be normalized if
                                                        possible before being compared (in the ``query`` and fields
                                                        being compared). The ``query`` is compared using prefix
                                                        matching against each portion of the artist (delimited by
                                                        whitespace).
============= ============= ============= ============= ===============================================================

Other Parameters
^^^^^^^^^^^^^^^^^^^^

.. include:: order_limit.rst


Example request
^^^^^^^^^^^^^^^

* http://localhost:8000/avalon/artists

* http://localhost:8000/avalon/artists?query=who

* http://localhost:8000/avalon/artists?order=id

* http://localhost:8000/avalon/artists?order=name&limit=10&offset=20


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
          "name": "Bad Religion",
          "id": "5cede078-e88e-5929-b8e1-cfda7992b8fd"
        },
        {
          "name": "Bad Brains",
          "id": "09b00809-23b3-50a3-a4ca-bba26d769c3b"
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
            "value": "foo",
            "field": "offset"
          },
          "message_key": "avalon.service.error.invalid_input_type",
          "message": "Invalid field value for integer field offset: 'foo'",
          "code": 101
        }
      ]
    }
