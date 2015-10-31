Songs endpoint
~~~~~~~~~~~~~~

The ``songs`` endpoint returns data for individual songs. The results returned
can be limited and filtered based on query string parameters.


Path and method
^^^^^^^^^^^^^^^

``GET /avalon/songs``

.. note::

    This path may be different depending on your ``REQUEST_PATH`` configuration setting.

Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

============= ============= ============= ============= ===============================================================
Name          Required?     Type          Mutiple?      Description
============= ============= ============= ============= ===============================================================
``album``     No            ``string``    No            Select only songs belonging to this album, exact match, not
                                                        case sensitive.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``album_id``  No            ``string``    No            Select only songs belonging to this album by UUID. The UUID is
                                                        expected to be formatted using hexadecimal digits or
                                                        hexadecimal digits with hyphens. If the UUID is not formatted
                                                        correctly error code ``101`` (invalid parameter type) will be
                                                        returned.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``artist``    No            ``string``    No            Select only songs by this artist, exact match, not case
                                                        sensitive.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``artist_id`` No            ``string``    No            Select only songs by this artist by UUID. The UUID is expected
                                                        to be formatted using hexadecimal digits or hexadecimal digits
                                                        with hyphens. If the UUID is not formatted correctly error code
                                                        ``101`` (invalid parameter type) will be returned.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``genre``     No            ``string``    No            Select only songs belonging to this genre, exact match, not
                                                        case sensitive.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``genre_id``  No            ``string``    No            Select only songs belonging to this genre by UUID. The UUID is
                                                        expected to be formatted using hexadecimal digits or
                                                        hexadecimal digits with hyphens. If the UUID is not formatted
                                                        correctly error code ``101`` (invalid parameter type) will be
                                                        returned.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``query``     No            ``string``    No            Select only songs whose album, artist, genre, or name contains
                                                        ``query``. The match is not case sensitive and unicode
                                                        characters will be normalized if possible before being compared
                                                        (in the ``query`` and fields being compared). The ``query`` is
                                                        compared using prefix matching against each portion of the
                                                        album, artist, genre, or song name (delimited by whitespace).
============= ============= ============= ============= ===============================================================

Other Parameters
^^^^^^^^^^^^^^^^

.. include:: order_limit.rst


Example requests
^^^^^^^^^^^^^^^^

* http://api.tshlabs.org/avalon/songs?artist=NOFX

* http://api.tshlabs.org/avalon/songs?artist_id=b048612e-1207-59f4-bbeb-ba0bc9a48cd1

* http://api.tshlabs.org/avalon/songs?query=Live&artist=The+Bouncing+Souls

* http://api.tshlabs.org/avalon/songs?album_id=2d24515c-a459-552a-b022-e85d1621425a

* http://api.tshlabs.org/avalon/songs?album_id=2d24515ca459552ab022e85d1621425a

* http://api.tshlabs.org/avalon/songs?genre=Ska

* http://api.tshlabs.org/avalon/songs?genre_id=8794d7b7-fff3-50bb-b1f1-438659e05fe5

* http://api.tshlabs.org/avalon/songs?query=anywhere


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
          "year": 2004,
          "track": 8,
          "name": "She's a Rebel",
          "album": "American Idiot",
          "album_id": "9ff51c16-2a7a-581c-b0b6-e28f5004139f",
          "artist": "Green Day",
          "artist_id": "b048612e-1207-59f4-bbeb-ba0bc9a48cd1",
          "genre": "Punk",
          "genre_id": "8794d7b7-fff3-50bb-b1f1-438659e05fe5",
          "id": "176cdea2-eb07-59ea-a809-2c6e23198cc8",
          "length": 120
        },
        {
          "year": 2002,
          "track": 11,
          "name": "Rotting",
          "album": "Shenanigans",
          "album_id": "9ddfbc73-6519-5ddf-a493-116cf3add9e1",
          "artist": "Green Day",
          "artist_id": "b048612e-1207-59f4-bbeb-ba0bc9a48cd1",
          "genre": "Punk",
          "genre_id": "8794d7b7-fff3-50bb-b1f1-438659e05fe5",
          "id": "840d20d8-58c6-50f6-b031-2a5a1b7c6f91",
          "length": 171
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
