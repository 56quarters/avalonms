#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


"""
Output all possible valid requests with query string params
to the songs endpoint
"""


from __future__ import print_function

import os
import os.path
import sys
import urllib

import avalon.exc
import avalon.models


try:
    db_url = sys.argv[1]
except IndexError:
    print("You must supply a DB connection URL!", file=sys.stderr)
    sys.exit(1)

try:
    handle = avalon.models.SessionHandler(db_url, None)
    handle.connect()
except avalon.exc.ConnectionError, e:
    print(str(e), file=sys.stderr)
    sys.exit(1)


song_base = 'http://localhost:8080/avalon/songs?'
album_base = 'http://localhost:8080/avalon/albums'
artist_base = 'http://localhost:8080/avalon/artists'
genre_base = 'http://localhost:8080/avalon/genres'

session = handle.get_session()
urls = []

for album in session.query(avalon.models.Album).all():
    urls.append(song_base + 'album=' + urllib.quote_plus(album.name.encode('utf-8')))
    urls.append(song_base + 'album=' + urllib.quote_plus(album.name.lower().encode('utf-8')))
    urls.append(song_base + 'album=' + urllib.quote_plus(album.name.upper().encode('utf-8')))
    urls.append(song_base + 'album_id=' + urllib.quote_plus(str(album.id)))
    urls.append(album_base)

for artist in session.query(avalon.models.Artist).all():
    urls.append(song_base + 'artist=' + urllib.quote_plus(artist.name.encode('utf-8')))
    urls.append(song_base + 'artist=' + urllib.quote_plus(artist.name.lower().encode('utf-8')))
    urls.append(song_base + 'artist=' + urllib.quote_plus(artist.name.upper().encode('utf-8')))
    urls.append(song_base + 'artist_id=' + urllib.quote_plus(str(artist.id)))
    urls.append(artist_base)

for genre in session.query(avalon.models.Genre).all():
    urls.append(song_base + 'genre=' + urllib.quote_plus(genre.name.encode('utf-8')))
    urls.append(song_base + 'genre=' + urllib.quote_plus(genre.name.lower().encode('utf-8')))
    urls.append(song_base + 'genre=' + urllib.quote_plus(genre.name.upper().encode('utf-8')))
    urls.append(song_base + 'genre_id=' + urllib.quote_plus(str(genre.id)))
    urls.append(genre_base)

handle.close(session)

for url in urls:
    print(url)

