Songs endpoint
~~~~~~~~~~~~~~

The ``songs`` endpoint returns data for individual songs. The results returned
can be limited and filtered based on query string parameters.


* Parameters

  - ``album`` 

    + Type: ``string``

    + Description: Select only songs belonging to this album (not case sensitive)

  - ``album_id``

    + Type: ``integer``

    + Description: Select only songs belonging to this album ID. A non-integer value
      will result in an error response.

  - ``artist``

    + Type: ``string``

    + Description: Select only songs by this artist (not case sensitive)

  - ``artist_id``

    + Type: ``integer``

    + Description: Select only songs by this artist ID. A non-integer value will
      result in an error response.

  - ``genre``

    + Type: ``string``

    + Description: Select only songs belonging to this genre (not case sensitive)

  - ``genre_id``

    + Type: ``integer``

    + Description: Select only songs belonging to this genre ID. A non-integer value
      will result in an error response.


* Possible error responses

  - ``InvalidParameterError``
    
    + Reason: An invalid value for query string parameter was passed.

    + HTTP Code: ``400``

  - ``ServerNotReadyError``

    + Reason: A request was made before the server finished starting.

    + HTTP Code: ``503``


* Success output format ::

    {
      "is_error": false,
      "error_name": "",
      "error_msg": "",
      "result_count": 2,
      "results": [
        {
          "id": 123,
          "name": "Basket Case",
          "year": 1994,
          "track": 7,
          "album": "Dookie",
          "artist": "Green Day",
          "genre": "Punk"
        },
        {
          "id": 456,
          "name": "She",
          "year": 1994,
          "track": 8,
          "album": "Dookie",
          "artist": "Green Day",
          "genre": "Punk"
        }
      ]
    }


* Error output format ::

    {
      "is_error": true,
      "error_name": "InvalidParameterError",
      "error_msg": "Invalid value for field [genre_id]",
      "result_count": 0,
      "results": []
    }


* Example Requests

  - ``http://localhost:8080/avalon/songs?artist=NOFX``

  - ``http://localhost:8080/avalon/songs?artist_id=123``

  - ``http://localhost:8080/avalon/songs?album=Live&artist=Bouncing+Souls``

  - ``http://localhost:8080/avalon/songs?album_id=456``

  - ``http://localhost:8080/avalon/songs?genre=Ska``

  - ``http://localhost:8080/avalon/songs?genre_id=1``
   

