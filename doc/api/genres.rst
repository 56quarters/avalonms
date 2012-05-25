Genres endpoint
~~~~~~~~~~~~~~~

The ``genres`` endpoint returns data for all the different genres that songs in
the music collection belong to.


* Parameters

  - The ``genres`` endpoint doesn't support any parameters and returns all genres.


* Possible error responses

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
          "name": "Punk"      
        },
        {
          "id": 456,
          "name": "Ska"
        }
      ]
    }


* Error output format ::

    {
      "is_error": true,
      "error_name": "ServerNotReadyError",
      "error_msg": "Server has not finished start up",
      "result_count": 0,
      "results": []
    }


* Example Request

  - ``http://localhost:8080/avalon/genres``


