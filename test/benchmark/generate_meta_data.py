#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from __future__ import unicode_literals, print_function
import sys
import argparse
import uuid
import random

import os
import codecs
from avalon import six
import avalon.app.scan
import avalon.cache
import avalon.models
import avalon.ids
import avalon.tags.insert
import avalon.tags.read


RATIO_ALBUMS = 0.06
RATIO_ARTISTS = 0.04
RATIO_GENRES = 0.01
RATIO_TRACKS = 0.89


def get_opts(prog):
    parser = argparse.ArgumentParser(
        prog=prog,
        description=__doc__)

    parser.add_argument(
        'word_list',
        help='Path to a word list file to use for generating fake '
             'music meta data, one word or phrase per line')

    parser.add_argument(
        'database',
        help='Path to a the SQLite database that fake meta data should '
             'be inserted into')

    return parser.parse_args()


class Partitioner(object):
    def __init__(self, base):
        self._base = base
        self._index = 0

    def take(self, n):
        start = self._index
        end = start + int(n)
        if end >= len(self._base):
            end = len(self._base) - 1
        self._index += end - start
        return list(self._base[start:end])


class MetadataBuilder(object):
    def __init__(self, tracks, albums, artists, genres):
        self._tracks = tracks
        self._albums = albums
        self._artists = artists
        self._genres = genres

    def get_metadata(self):
        out = []
        for track in self._tracks:
            out.append(self._get_one(track))
        return out

    def _get_one(self, track):
        return avalon.tags.read.Metadata(
            path=six.text_type(uuid.uuid4()),
            album=random.choice(self._albums),
            artist=random.choice(self._artists),
            genre=random.choice(self._genres),
            title=track,
            track=random.randint(1, 30),
            year=random.randint(1970, 2038),
            length=random.randint(10, 500))


def main():
    prog = os.path.basename(sys.argv[0])
    args = get_opts(prog)

    lines = []

    try:
        with codecs.open(args.word_list, encoding='utf-8') as handle:
            for line in handle:
                lines.append(line.strip())
    except IOError as e:
        print('{0}: Could not open word list: {1}'.format(prog, e), file=sys.stderr)
        return 1

    total_lines = len(lines)
    random.shuffle(lines)
    partitioner = Partitioner(lines)
    albums = partitioner.take(RATIO_ALBUMS * total_lines)
    artists = partitioner.take(RATIO_ARTISTS * total_lines)
    genres = partitioner.take(RATIO_GENRES * total_lines)
    tracks = partitioner.take(RATIO_TRACKS * total_lines)

    builder = MetadataBuilder(tracks, albums, artists, genres)
    tags = builder.get_metadata()

    session_config = avalon.models.SessionHandlerConfig()
    session_config.engine = avalon.models.get_engine('sqlite:///{0}'.format(args.database))
    session_config.metadata = avalon.models.get_metadata()
    session_config.session_factory = avalon.models.get_session_factory()

    handler = avalon.models.SessionHandler(session_config)
    handler.connect()

    read_dao = avalon.models.ReadOnlyDao(handler)
    id_cache = avalon.cache.IdLookupCache(read_dao)

    with handler.scoped_session(read_only=False) as session:
        cleaner = avalon.tags.insert.Cleaner(session)
        cleaner.clean_type(avalon.models.Album)
        cleaner.clean_type(avalon.models.Artist)
        cleaner.clean_type(avalon.models.Genre)
        cleaner.clean_type(avalon.models.Track)

        field_loader = avalon.tags.insert.TrackFieldLoader(session, tags)
        field_loader.insert(avalon.models.Album, avalon.ids.get_album_id, 'album')
        field_loader.insert(avalon.models.Artist, avalon.ids.get_artist_id, 'artist')
        field_loader.insert(avalon.models.Genre, avalon.ids.get_genre_id, 'genre')

        id_cache.reload(session=session)
        track_loader = avalon.tags.insert.TrackLoader(session, tags, id_cache)
        track_loader.insert(avalon.models.Track, avalon.ids.get_track_id)

    return 0


if __name__ == '__main__':
    sys.exit(main())
