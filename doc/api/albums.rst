Albums endpoint
~~~~~~~~~~~~~~~

The ``albums`` endpoint returns data for all the different albums that songs
in the music collection belong to.


* Parameters

  - The ``albums`` endpoint doesn't support any parameters and returns all albums.


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
          "name": "Dookie"      
        },
        {
          "id": 456,
          "name": "Insomniac"
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

  - ``http://localhost:8080/avalon/albums``

