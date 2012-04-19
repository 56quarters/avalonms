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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import avalon.models


try:
    db_path = sys.argv[1]
except IndexError:
    print("You must supply a path to the DB!", file=sys.stderr)
    sys.exit(1)


song_base = 'http://localhost:8080/avalon/songs?'
album_base = 'http://localhost:8080/avalon/albums'
artist_base = 'http://localhost:8080/avalon/artists'
genre_base = 'http://localhost:8080/avalon/genres'

handle = avalon.models.SessionHandler('sqlite:///%s' % db_path)
handle.connect()

session = handle.get_session()
urls = []

for album in session.query(avalon.models.Album).all():
    urls.append(song_base + 'album=' + urllib.quote_plus(album.name.encode('utf-8')))
    urls.append(song_base + 'album_id=' + urllib.quote(str(album.id)))
    urls.append(album_base)

for artist in session.query(avalon.models.Artist).all():
    urls.append(song_base + 'artist=' + urllib.quote(artist.name.encode('utf-8')))
    urls.append(song_base + 'artist_id=' + urllib.quote(str(artist.id)))
    urls.append(artist_base)

for genre in session.query(avalon.models.Genre).all():
    urls.append(song_base + 'genre=' + urllib.quote(genre.name.encode('utf-8')))
    urls.append(song_base + 'genre_id=' + urllib.quote(str(genre.id)))
    urls.append(genre_base)

handle.close(session)

for url in urls:
    print(url)

