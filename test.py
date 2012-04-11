# -*- coding: utf-8 -*-

import os.path

import avalonms.scan
import avalonms.models


root ='music/audio'
#root  ='music/audio/CIVET'
files = avalonms.scan.get_files(
    os.path.join(os.path.expanduser('~'), root))
tags = avalonms.scan.get_tags(files)


artists = set()
albums = set()
genres = set()
tracks = []


for data in tags.values():
    track = avalonms.models.Track()
    track.name = data.title
    track.track = data.track
    track.year = data.year
    tracks.append(track)


handler = avalonms.models.SessionHandler()
handler.connect()
handler.create_tables()

sess = handler.get_session()
sess.add_all(tracks)
sess.commit()
