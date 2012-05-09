Avalon Music Server
===================

The Avalon Music Server is a BSD licensed server that scans metadata
from a music collection and provides a JSON interface to it over HTTP.


Requirements
------------

* Python >= 2.6
* Argparse >= 1.2.0 (Or Python 2.7)
* CherryPy >= 3.2.0
* Tagpy >= 0.94


Installation
------------

  wget http://cdn.tshlabs.org/dist/avalonms/avalonms-0.1.0.tar.bz2

  tar -xvjf avalonms-0.1.0.tar.bz2

  cd avalonms-0.1.0

  sudo python setup.py install

Or

  pip install avalonms

Eratta
------

* The server cannot be run as root, it must be run as an unprivileged user.
* Consequently, the server cannot run on a privileged port (< 1024).

Usage
-----

Arguments
~~~~~~~~~

* ``collection`` - Path to the root of your music collection to scan

Options
~~~~~~~

* ``--access-log=PATH`` - Path to a file to use for logging requests to the server.

* ``--daemon`` - Fork into the background and run as a daemon.

.. * ``--daemon-user=USER`` - Run the server as this user. The server will switch to this non-privileged user when started as root and run in daemon mode.

.. * ``--daemon-group=GROUP`` - Run the server as this group. The server will switch to this non-privileged group when started as root and run in daemon mode.

* ``--db-path=PATH`` - Path to a file to use for the the backing SQLite database for storing collection metadata.

* ``--error-log=PATH`` - Path to a file to use for server errors and application informational logging.

* ``--no-scan`` - If present, don't remove existing information about the music collection and rescan it.

* ``--server-address=ADDR`` - Interface address to bind the server to. IPv4 and IPv6 addresses are supported. Default is localhost IPv4.

* ``--server-port=PORT`` - Port to listen for requests on. Default is port 8080.

* ``--server-queue=NUM`` - The number of incoming connections to the server to allow to be queued.

* ``--server-threads=NUM`` - The number of threads to use to process incoming requests for the server.


API
---

The Avalon Music Server handles requests on the specified interface and
port at the path ``/avalon``. Available endpoints are:

* ``/avalon/songs``

* ``/avalon/albums``

* ``/avalon/artists``

* ``/avalon/genres``

      
Songs endpoint
~~~~~~~~~~~~~~

* Parameters: 

  - ``album`` 

    + Type: ``string``

    + Description: Select only songs belonging to this album (not case sensitive)

  - ``album_id``

    + Type: ``integer``

    + Description: Select only songs belonging to this album ID

  - ``artist``

    + Type: ``string``

    + Description: Select only songs by this artist (not case sensitive)

  - ``artist_id``

    + Type: ``integer``

    + Description: Select only songs by this artist ID

  - ``genre``

    + Type: ``string``

    + Description: Select only songs belonging to this genre (not case sensitive)

  - ``genre_id``

    + Type: ``integer``

    + Description: Select only songs belonging to this genre ID


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

* Example Requests

  - ``http://localhost:8080/avalon/songs?artist=NOFX``

  - ``http://localhost:8080/avalon/songs?artist_id=123``

  - ``http://localhost:8080/avalon/songs?album=Live&artist=Bouncing+Souls``

  - ``http://localhost:8080/avalon/songs?album_id=456``

  - ``http://localhost:8080/avalon/songs?genre=Ska``

  - ``http://localhost:8080/avalon/songs?genre_id=1``
   

Albums endpoint
~~~~~~~~~~~~~~~

* Parameters

  - The ``albums`` endpoint doesn't support any parameters and returns all albums.


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

* Example Request

  - ``http://localhost:8080/avalon/albums``


Artists endpoint
~~~~~~~~~~~~~~~~

* Parameters

  - The ``artists`` endpoint doesn't support any parameters and returns all artists.


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

* Example Request

  - ``http://localhost:8080/avalon/artists``


Genre endpoint
~~~~~~~~~~~~~~

* Parameters

  - The ``genre`` endpoint doesn't support any parameters and returns all genres.


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

* Example Request

  - ``http://localhost:8080/avalon/genres``


