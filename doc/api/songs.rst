Songs endpoint
~~~~~~~~~~~~~~

The ``songs`` endpoint returns data for individual songs. The results returned
can be limited and filtered based on query string parameters.


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
                                                        correctly an ``INVALID_PARAMETER_ERROR`` will be returned.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``artist``    No            ``string``    No            Select only songs by this artist, exact match, not case
                                                        sensitive.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``artist_id`` No            ``string``    No            Select only songs by this artist by UUID. The UUID is expected
                                                        to be formatted using hexadecimal digits or hexadecimal digits
                                                        with hyphens. If the UUID is not formatted correctly an
                                                        ``INVALID_PARAMETER_ERROR`` will be returned.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``genre``     No            ``string``    No            Select only songs belonging to this genre, exact match, not
                                                        case sensitive.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``genre_id``  No            ``string``    No            Select only songs belonging to this genre by UUID. The UUID is
                                                        expected to be formatted using hexadecimal digits or
                                                        hexadecimal digits with hyphens. If the UUID is not formatted
                                                        correctly an ``INVALID_PARAMETER_ERROR`` will be
                                                        returned.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``query``     No            ``string``    No            Select only songs whose album, artist, genre, or name contains
                                                        ``query``. The match is not case sensitive and unicode
                                                        characters will be normalized if possible before being compared
                                                        (in the ``query`` and fields being compared). The ``query`` is
                                                        compared using prefix matching against each portion of the
                                                        album, artist, genre, or song name (delimitted by whitespace).
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
          "id": "597f5485-f046-5a54-bb60-7bc60be5c2a1",
          "name": "Basket Case",
          "length": 183,
          "year": 1994,
          "track": 7,
          "album": "Dookie",
          "album_id": "2d24515c-a459-552a-b022-e85d1621425a",
          "artist": "Green Day",
          "artist_id": "b048612e-1207-59f4-bbeb-ba0bc9a48cd1",
          "genre": "Punk",
          "genre_id": "8794d7b7-fff3-50bb-b1f1-438659e05fe5"
        },
        {
          "id": "ffaa2a77-2482-5999-b8cd-be5caf4b994e",
          "name": "She",
          "length": 134,
          "year": 1994,
          "track": 8,
          "album": "Dookie",
          "album_id": "2d24515c-a459-552a-b022-e85d1621425a",
          "artist": "Green Day",
          "artist_id": "b048612e-1207-59f4-bbeb-ba0bc9a48cd1",
          "genre": "Punk",
          "genre_id": "8794d7b7-fff3-50bb-b1f1-438659e05fe5"

        }
      ]
    }


Error output format
^^^^^^^^^^^^^^^^^^^

  ::  

    {
      "is_error": true,
      "error_name": "INVALID_PARAMETER_ERROR",
      "error_msg": "Invalid value for field [limit]",
      "result_count": 0,
      "results": []
    }


