# -*- coding: utf-8 -*-

import os.path

import avalon.models
import avalon.scan
import avalon.services


handler = avalon.models.SessionHandler()
handler.connect()
handler.create_tables()

sess = handler.get_session()

root = 'music/audio'
files = avalon.scan.get_files(os.path.join(os.path.expanduser('~'), root))
tags = avalon.scan.get_tags(files)

service = avalon.services.InsertService(tags.values(), sess)
service.insert_tracks()
