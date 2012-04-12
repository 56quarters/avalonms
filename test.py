# -*- coding: utf-8 -*-

import os.path

import avalonms.models
import avalonms.scan
import avalonms.services


handler = avalonms.models.SessionHandler()
handler.connect()
handler.create_tables()

sess = handler.get_session()

root = 'music/audio'
files = avalonms.scan.get_files(
    os.path.join(os.path.expanduser('~'), root))
tags = avalonms.scan.get_tags(files)

service = avalonms.services.InsertService(tags.values(), sess)
service.insert_tracks()
