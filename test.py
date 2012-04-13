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

root = 'music/audio'
files = avalon.scan.get_files(os.path.join(os.path.expanduser('~'), root))
tags = avalon.scan.get_tags(files)

service = avalon.services.InsertService(tags.values(), handler)
service.insert_tracks()

web = avalon.web.AvalonHandler(handler)
cherrypy.quickstart(web)
