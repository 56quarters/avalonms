#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


"""
Output valid requests with query string params to each of the
metadata endpoints.
"""


from __future__ import print_function

import sys
import urllib

import avalon.exc
import avalon.models


try:
    db_url = sys.argv[1]
except IndexError:
    print("You must supply a DB connection URL!", file=sys.stderr)
    sys.exit(1)

config = avalon.models.SessionHandlerConfig()
config.engine = avalon.models.get_engine(db_url)
config.session_factory = avalon.models.get_session_factory()
config.metadata = avalon.models.get_metadata()
config.log = None

try:
    handle = avalon.models.SessionHandler(config)
    handle.connect()
except avalon.exc.ConnectionError, e:
    print(str(e), file=sys.stderr)
    sys.exit(1)


song_base = 'http://localhost:8080/avalon/songs?'
album_base = 'http://localhost:8080/avalon/albums?'
artist_base = 'http://localhost:8080/avalon/artists?'
genre_base = 'http://localhost:8080/avalon/genres?'

session = handle.get_session()
urls = set()

for album in session.query(avalon.models.Album).all():
    urls.add(song_base + 'album=' + urllib.quote_plus(album.name.encode('utf-8')))
    urls.add(song_base + 'album=' + urllib.quote_plus(album.name.lower().encode('utf-8')))
    urls.add(song_base + 'album=' + urllib.quote_plus(album.name.upper().encode('utf-8')))
    urls.add(song_base + 'album_id=' + urllib.quote_plus(str(album.id)))
    urls.add(album_base + 'order=name' )
    for term in album.name.split():
        urls.add(album_base + 'query=' + urllib.quote_plus(term.encode('utf-8')))
        urls.add(song_base + 'query=' + urllib.quote_plus(term.encode('utf-8')))

for artist in session.query(avalon.models.Artist).all():
    urls.add(song_base + 'artist=' + urllib.quote_plus(artist.name.encode('utf-8')))
    urls.add(song_base + 'artist=' + urllib.quote_plus(artist.name.lower().encode('utf-8')))
    urls.add(song_base + 'artist=' + urllib.quote_plus(artist.name.upper().encode('utf-8')))
    urls.add(song_base + 'artist_id=' + urllib.quote_plus(str(artist.id)))
    urls.add(artist_base + 'order=name')
    for term in artist.name.split():
        urls.add(artist_base + 'query=' + urllib.quote_plus(term.encode('utf-8')))
        urls.add(song_base + 'query=' + urllib.quote_plus(term.encode('utf-8')))

for genre in session.query(avalon.models.Genre).all():
    urls.add(song_base + 'genre=' + urllib.quote_plus(genre.name.encode('utf-8')))
    urls.add(song_base + 'genre=' + urllib.quote_plus(genre.name.lower().encode('utf-8')))
    urls.add(song_base + 'genre=' + urllib.quote_plus(genre.name.upper().encode('utf-8')))
    urls.add(song_base + 'genre_id=' + urllib.quote_plus(str(genre.id)))
    urls.add(genre_base + 'order=name')
    for term in genre.name.split():
        urls.add(genre_base + 'query=' + urllib.quote_plus(term.encode('utf-8')))
        urls.add(song_base + 'query=' + urllib.quote_plus(term.encode('utf-8')))

for song in session.query(avalon.models.Track).all():
    for term in song.name.split():
        urls.add(song_base + 'query=' + urllib.quote_plus(term.encode('utf-8')))

handle.close(session)

for url in urls:
    print(url)

