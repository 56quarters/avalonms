# -*- coding: utf-8 -*-

import os.path

import cherrypy

import avalon.models
import avalon.scan
import avalon.services
import avalon.web


handler = avalon.models.SessionHandler()
handler.connect()
handler.create_tables()

sess = handler.get_session()

root = 'music/audio'
files = avalon.scan.get_files(os.path.join(os.path.expanduser('~'), root))
tags = avalon.scan.get_tags(files)

service = avalon.services.InsertService(tags.values(), sess)
service.insert_tracks()


tracks = sess.query(avalon.models.Track).filter(avalon.models.Track.genre_id == 4).all()

print [track.to_json() for track in tracks]

web = avalon.web.AvalonHandler(handler)
cherrypy.quickstart(web)
