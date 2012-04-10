# -*- coding: utf-8 -*-

import avalonms.scan
files = avalonms.scan.get_files('/home/pillin/music/audio/CIVET')
tags = avalonms.scan.get_tags(files)

print tags
