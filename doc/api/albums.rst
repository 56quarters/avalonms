Albums endpoint
~~~~~~~~~~~~~~~

The ``albums`` endpoint returns data for all the different albums that songs
in the music collection belong to.


Filtering Parameters
^^^^^^^^^^^^^^^^^^^^

* ``query``

  + Type: ``string``

  + Description: Select only albums whose name contains ``query``. The match
    is not case sensitive and unicode characters will be normalized if possible
    before being compared (in the ``query`` and fields being compared). The
    ``query`` is compared using prefix matching against each portion of the
    album name (delimitted by whitespace).

Other Parameters
^^^^^^^^^^^^^^^^

.. include:: order_limit.rst


Example request
^^^^^^^^^^^^^^^

* http://api.tshlabs.org/avalon/albums

* http://api.tshlabs.org/avalon/albums?query=live

* http://api.tshlabs.org/avalon/albums?order=name&direction=asc

* http://api.tshlabs.org/avalon/albums?order=name&direction=desc&limit=5


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



