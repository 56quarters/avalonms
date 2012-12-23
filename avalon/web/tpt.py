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


"""Templates used by the status endpoints."""


__all__ = [
    'STATUS_TPT'
    ]


# TODO: Move this to a datafile
STATUS_TPT = """
<!DOCTYPE html>
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
    .not.ready .status {
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
    <dd class="status">%(status)s</dd>

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
