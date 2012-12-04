# -*- coding: utf-8 -*-
#
# Avalon Music Server
#
# Copyright (c) 2012 TSH Labs <projects@tshlabs.org>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


""" """


import functools
from datetime import datetime

import avalon.util


__all__ = [
    'intersection',
    'AvalonApiEndpoints',
    'AvalonApiEndpointsConfig'
    'AvalonStatusEndpoints',
    'AvalonStatusEndpointsConfig'
    ]


def intersection(sets):
    """Find the intersection of all of the given non-None sets."""
    # NOTE: we use 'not None' here instead of a simple boolean test
    # because we want the intersection with an empty set to actually
    # mean 'there were 0 results'.
    return functools.reduce(
        lambda x, y: x.intersection(y),
        [res_set for res_set in sets if res_set is not None])


class AvalonApiEndpointsConfig(object):

    """Configuration for the metadata endpoints."""

    def __init__(self):
        self.track_store = None
        self.album_store = None
        self.artist_store = None
        self.genre_store = None
        self.id_cache = None


class AvalonApiEndpoints(object):

    """Endpoints for querying in memory stores of audio metadata."""

    def __init__(self, config):
        """Initialize each of the stores by loading from the database."""
        self._tracks = config.track_store
        self._albums = config.album_store
        self._artists = config.artist_store
        self._genres = config.genre_store
        self._id_cache = config.id_cache

    def reload(self):
        """Reload in memory stores from the database."""
        self._tracks.reload()
        self._albums.reload()
        self._artists.reload()
        self._genres.reload()
        self._id_cache.reload()

    def get_albums(self):
        """Return a list of all albums."""
        return self._albums.all()

    def get_artists(self):
        """Return a list of all artists."""
        return self._artists.all()

    def get_genres(self):
        """Return a list of all genres."""
        return self._genres.all()

    def get_songs(self, params):
        """Return song results based on the given query string parameters."""
        sets = []

        if None is not params.get('album'):
            sets.append(
                self._tracks.by_album(
                    self._id_cache.get_album_id(params.get('album'))))
        if None is not params.get('artist'):
            sets.append(
                self._tracks.by_artist(
                    self._id_cache.get_artist_id(params.get('artist'))))
        if None is not params.get('genre'):
            sets.append(
                self._tracks.by_genre(
                    self._id_cache.get_genre_id(params.get('genre'))))

        if None is not params.get('album_id'):
            sets.append(self._tracks.by_album(params.get('album_id')))
        if None is not params.get('artist_id'):
            sets.append(self._tracks.by_artist(params.get('artist_id')))
        if None is not params.get('genre_id'):
            sets.append(self._tracks.by_genre(params.get('genre_id')))
            
        if sets:
            # Return the intersection of any non-None sets
            return intersection(sets)
        # There were no parameters to filter songs by any criteria
        return self._tracks.all()



class AvalonStatusEndpointsConfig(object):

    """Configuration for the status endpoints."""

    def __init__(self):
        self.ready = None


class AvalonStatusEndpoints(object):

    """Status endpoints for information about the running application."""

    def __init__(self, config):
        """Initialize the ready state of the server."""
        self._ready = config.ready

    def _get_ready(self):
        """Get the ready state of the application."""
        return self._ready.is_set()

    def _set_ready(self, val):
        """Set the ready state of the application."""
        if val:
            self._ready.set()
        else:
            self._ready.clear()

    ready = property(
        _get_ready, _set_ready, None, "Is the application ready")

    def reload(self):
        pass

    def get_status_page(self, startup, api):
        """ """
        return _STATUS_PAGE_TPT % {
            'status': 'ready' if self.ready else 'not ready',
            'user': avalon.util.get_current_uname(),
            'group': avalon.util.get_current_gname(),
            'uptime': datetime.utcnow() - startup,
            'memory': avalon.util.get_mem_usage(),
            'threads': '<br />'.join(avalon.util.get_thread_names()),
            'albums': len(api.get_albums()),
            'artists': len(api.get_artists()),
            'genres': len(api.get_genres()),
            'tracks': 0
            }

    def get_heartbeat(self):
        if self.ready:
            return "OKOKOK"
        return "NONONO"

#
#
#
_STATUS_PAGE_TPT = """<!DOCTYPE html>
<html>
<head>
  <title>Avalon Music Server</title>
  <style type="text/css">
    body {
      background-color: #363636;
      color: #E7E7E7;
      font-family: helvetica, arial, sans-serif;
      font-size: 14px;
      line-height: 20px;
    }
    h1 {
      border-bottom: 1px solid #FFF;
      color: #00ADEE;
      margin-top: 10px;
      padding-bottom: 15px;
      text-shadow: 0 0 1px #444;
    }
    dt {
      color: #00ADEE;
      font-weight: bold;
      margin-top: 10px;
    }
    .stats {
      background-color: #171717;
      border: 1px solid #FFF;
      border-radius: 15px;
      box-shadow: 0 3px 3px 3px #444;
      margin: 50px auto;
      padding: 15px;
      width: 500px;
    }
    .status {
      text-transform: uppercase;
    }
    .status.not.ready {
      color: #C00;
      font-weight: bold;
     }
  </style>
</head>
<body class="%(status)s">
  <div class="stats">
  <h1>Avalon Music Server</h1>
  <dl>
    <dt>Server is:</dt>
    <dd class="status %(status)s">%(status)s</dd>

    <dt>Running as:</dt>
    <dd>%(user)s:%(group)s</dd>

    <dt>Uptime:</dt>
    <dd>%(uptime)s</dd>

    <dt>Memory:</dt>
    <dd>%(memory)s MB</dd>

    <dt>Threads:</dt>
    <dd>%(threads)s</dd>

    <dt>Loaded:</dt>
    <dd>
      Albums: %(albums)s<br /> 
      Artists: %(artists)s<br /> 
      Genres: %(genres)s<br /> 
      Tracks: %(tracks)s<br />
    </dd>
  </dl>
  </div>
</body>
</html>
"""

