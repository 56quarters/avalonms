Usage
-----

Running The Server
~~~~~~~~~~~~~~~~~~


Running In The Foreground
=========================


Running As A Daemon
===================


Running As A Daemon Started As Root
===================================


Arguments
~~~~~~~~~

* ``collection`` - Path to the root of your music collection to scan

Options
~~~~~~~

* ``--access-log=PATH`` - Path to a file to use for logging requests to the server.

* ``--daemon`` - Fork into the background and run as a daemon.

* ``--daemon-user=USER`` - Run the server as this user. The server will switch to this non-privileged user when started as root and run in daemon mode.

* ``--daemon-group=GROUP`` - Run the server as this group. The server will switch to this non-privileged group when started as root and run in daemon mode.

* ``--db-path=PATH`` - Path to a file to use for the the backing SQLite database for storing collection metadata.

* ``--error-log=PATH`` - Path to a file to use for server errors and application informational logging.

* ``--no-scan`` - Do not rescan and rebuild the music collection at server start or durning any reloads of the server (graceful events).

* ``--server-address=ADDR`` - Interface address to bind the server to. IPv4 and IPv6 addresses are supported. Default is localhost IPv4.

* ``--server-port=PORT`` - Port to listen for requests on. Default is port 8080.

* ``--server-queue=NUM`` - The number of incoming connections to the server to allow to be queued.

* ``--server-threads=NUM`` - The number of threads to use to process incoming requests for the server.

