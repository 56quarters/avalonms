Genres endpoint
~~~~~~~~~~~~~~~

The ``genres`` endpoint returns data for all the different genres that songs in
the music collection belong to.


Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

* ``query``

  + Type: ``string``

  + Description: Select only genres whose name contains ``query`` (not case sensitive).

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
          "id": 123,
          "name": "Punk"      
        },
        {
          "id": 456,
          "name": "Ska"
        }
      ]
    }


Error output format
^^^^^^^^^^^^^^^^^^^

  ::

    {
      "is_error": true,
      "error_name": "ServerNotReadyError",
      "error_msg": "Server has not finished start up",
      "result_count": 0,
      "results": []
    }


Example request
^^^^^^^^^^^^^^^

* http://api.tshlabs.org/avalon/genres

* http://api.tshlabs.org/avalon/genres?query=rock

* http://api.tshlabs.org/avalon/genres?order=name

* http://api.tshlabs.org/avalon/genres?order=name&limit=10


