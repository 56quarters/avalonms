# -*- coding: utf-8 -*-

import avalonms.scan
import avalonms.models

files = avalonms.scan.get_files('/home/pillin/music/audio/CIVET')
tags = avalonms.scan.get_tags(files)
insert = []

for data in tags.values():
    track = avalonms.models.Track()
    track.name = data.title
    track.track = data.track
    track.year = data.year
    insert.append(track)

handler = avalonms.models.SessionHandler()
handler.connect()
handler.create_tables()

sess = handler.get_session()
sess.add_all(insert)
sess.commit()
