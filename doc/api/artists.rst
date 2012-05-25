Artists endpoint
~~~~~~~~~~~~~~~~

The ``artists`` endpoint returns data for all the different artists that songs
in the music collection are performed by.


* Parameters

  - The ``artists`` endpoint doesn't support any parameters and returns all artists.


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
          "name": "Green Day"      
        },
        {
          "id": 456,
          "name": "Bad Religion"
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

  - ``http://localhost:8080/avalon/artists``
