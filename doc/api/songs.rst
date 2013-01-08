Songs endpoint
~~~~~~~~~~~~~~

The ``songs`` endpoint returns data for individual songs. The results returned
can be limited and filtered based on query string parameters.


Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

* ``album`` 

  + Type: ``string``

  + Description: Select only songs belonging to this album (not case sensitive)

* ``album_id``

  + Type: ``string``

  + Description: Select only songs belonging to this album by UUID.

* ``artist``

  + Type: ``string``

  + Description: Select only songs by this artist (not case sensitive)

* ``artist_id``

  + Type: ``string``

  + Description: Select only songs by this artist by UUID.

* ``genre``

  + Type: ``string``

  + Description: Select only songs belonging to this genre (not case sensitive)

* ``genre_id``

  + Type: ``string``

  + Description: Select only songs belonging to this genre by UUID.

* ``query``

  + Type: ``string``

  + Description: Select only songs whose album, artist, genre, or name contains ``query`` (not case sensitive).

Other Parameters
^^^^^^^^^^^^^^^^

.. include:: order_limit.rst



Possible error responses
^^^^^^^^^^^^^^^^^^^^^^^^

* ``InvalidParameterError``
    
  + Reason: An invalid value for query string parameter was passed.

* ``ServerNotReadyError``

  + Reason: A request was made before the server finished starting.


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
      "error_name": "InvalidParameterError",
      "error_msg": "Invalid value for field [limit]",
      "result_count": 0,
      "results": []
    }


Example requests
^^^^^^^^^^^^^^^^

* http://api.tshlabs.org/avalon/songs?artist=NOFX

* http://api.tshlabs.org/avalon/songs?artist_id=b048612e-1207-59f4-bbeb-ba0bc9a48cd1

* http://api.tshlabs.org/avalon/songs?query=Live&artist=The+Bouncing+Souls

* http://api.tshlabs.org/avalon/songs?album_id=2d24515c-a459-552a-b022-e85d1621425a

* http://api.tshlabs.org/avalon/songs?genre=Ska

* http://api.tshlabs.org/avalon/songs?genre_id=8794d7b7-fff3-50bb-b1f1-438659e05fe5

* http://api.tshlabs.org/avalon/songs?query=anywhere
   

