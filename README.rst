Avalon Music Server
===================

The Avalon Music Server is a BSD licensed server that scans metadata
from a music collection and provides a JSON interface to it over HTTP.

Requirements
------------

- Python >= 2.7
- Tagpy >= 0.94
- CherryPy >= 3.2.0

Installation
------------

- Stuff

Usage
-----

- Stuff

API
---

The Avalon Music server handles requests on the specified interface and
port at the path '/avalon'. Available endpoints: ::

   http://host:port/avalon/songs

   http://host:port/avalon/albums

   http://host:port/avalon/artists

   http://host:port/avalon/genres
      
Songs endpoint
~~~~~~~~~~~~~~

- Output Format
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


   
