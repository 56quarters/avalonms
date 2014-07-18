UUID Generation
---------------

The Avalon Music Server uses UUIDs (version 5) to act as unique identifiers for albums,
artists, genres, and tracks. If you wish to generate compatible IDs outside of the Avalon
Music Server the process is as follows (in Python):


Albums
======

Album IDs are generated from the lowercase, UTF-8 encoded, name of the album.

The namespace UUID is ``7655e605-6eaa-40d8-a25f-5c6c92a4d31a``.

>>> import uuid
>>> album_namespace = uuid.UUID('7655e605-6eaa-40d8-a25f-5c6c92a4d31a')
>>> album_name = u'¡Uno!'.lower().encode('utf-8')
>>> album_id = uuid.uuid5(album_namespace, album_name)
>>> album_id
UUID('32792eb5-03ff-5837-9869-d77ac9b5c99f')

Artists
=======

Artist IDs are generated from the lowercase, UTF-8 encoded, name of the artist.

The namespace UUID is ``fe4df0f6-2c55-4ba6-acf3-134eae3e710e``.

>>> import uuid
>>> artist_namespace = uuid.UUID('fe4df0f6-2c55-4ba6-acf3-134eae3e710e')
>>> artist_name = u'Minor Threat'.lower().encode('utf-8')
>>> artist_id = uuid.uuid5(artist_namespace, artist_name)
>>> artist_id
UUID('debcc564-211b-559c-b810-e72598bdaf47')

Genres
======

Genre IDs are generated from the lowercase, UTF-8 encoded, name of the genre.

The namespace UUID is ``dd8dbd9c-8ed7-4719-80c5-71d978665dd0``.

>>> import uuid
>>> genre_namespace = uuid.UUID('dd8dbd9c-8ed7-4719-80c5-71d978665dd0')
>>> genre_name = u'Punk Ska'.lower().encode('utf-8')
>>> genre_id = uuid.uuid5(genre_namespace, genre_name)
>>> genre_id
UUID('3af7ba62-d87f-5258-af62-d7c5655ec567')

Songs
=====

Song IDs are generated from the case sensitive path of the file, encoded as UTF-8.

The namespace UUID is ``4151ace3-6a98-41cd-a3de-8c242654cb67``.

>>> import uuid
>>> song_namespace = uuid.UUID('4151ace3-6a98-41cd-a3de-8c242654cb67')
>>> song_path = u'/music/Voodoo_Glow_Skulls/02-adicción,_tradición,_revolución.ogg'.encode('utf-8')
>>> song_id = uuid.uuid5(song_namespace, song_path)
>>> song_id
UUID('56b33b92-d5b6-5971-b166-dc959b442c0c')
  

