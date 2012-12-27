Albums endpoint
~~~~~~~~~~~~~~~

The ``albums`` endpoint returns data for all the different albums that songs
in the music collection belong to.


Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

* ``query``

  + Type: ``string``

  + Description: Select only albums whose name contains ``query`` (not case sensitive).

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
          "name": "Dookie"      
        },
        {
          "id": 456,
          "name": "Insomniac"
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

* ``http://localhost:8080/avalon/albums``

* ``http://localhost:8080/avalon/albums?query=live``

* ``http://localhost:8080/avalon/albums?order=name&direction=asc``

* ``http://localhost:8080/avalon/albums?order=name&direction=desc&limit=5``

