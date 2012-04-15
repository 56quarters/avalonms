Avalon Music Server
===================

The Avalon Music Server is a BSD licensed server that scans metadata
from a music collection and provides a JSON interface to it over HTTP.

Requirements
------------

- Python >= 2.6
- Argparse >= 1.2.0 (Or Python 2.7)
- CherryPy >= 3.2.0
- Tagpy >= 0.94


Installation
------------

  python setup.py install

  pip install avalonms


Usage
-----

- Stuff

API
---

The Avalon Music Server handles requests on the specified interface and
port at the path ``/avalon``. Available endpoints:

* ``/avalon/songs``

* ``/avalon/albums``

* ``/avalon/artists``

* ``/avalon/genres``
      
Songs endpoint
~~~~~~~~~~~~~~

* Parameters: 

  - ``album`` 

    + Type: ``string``

    + Description: Select only songs belonging to this album (case sensitive)

  - ``album_id``

    + Type: ``integer``

    + Description: Select only songs belonging to this album ID

  - ``artist``

    + Type: ``string``

    + Description: Select only songs by this artist (case sensitive)

  - ``artist_id``

    + Type: ``integer``

    + Description: Select only songs by this artist ID

  - ``genre``

    + Type: ``string``

    + Description: Select only songs belonging to this genre (case sensitive)

  - ``genre_id``

    + Type: ``integer``

    + Description: Select only songs belonging to this genre ID


* Output Format ::

    [
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


* Output Format ::

    [
      {
        "id": 123,
        "name": "Dookie"      
      },
      {
        "id": 456,
        "name": "Insomniac"
      }
    ]

* Example Requests

  - ``http://localhost:8080/avalon/albums``


Artists endpoint
~~~~~~~~~~~~~~~~

* Parameters

  - The ``artists`` endpoint doesn't support any parameters and returns all artists.


* Output Format ::

    [
      {
        "id": 123,
        "name": "Green Day"      
      },
      {
        "id": 456,
        "name": "Bad Religion"
      }
    ]

* Example Requests

  - ``http://localhost:8080/avalon/artists``


Genre endpoint
~~~~~~~~~~~~~~

* Parameters

  - The ``genre`` endpoint doesn't support any parameters and returns all genres.


* Output Format ::

    [
      {
        "id": 123,
        "name": "Punk"      
      },
      {
        "id": 456,
        "name": "Ska"
      }
    ]

* Example Requests

  - ``http://localhost:8080/avalon/genres``


