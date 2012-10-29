Usage
-----

Running The Server
~~~~~~~~~~~~~~~~~~

The Avalon Music Server can be run in the foreground or in the background as a UNIX 
daemon. It can be run as an unprivileged user, as the super user (not recommended), 
or can start as the super user and switch to an unprivileged user. It can scan your
music collection at start up or just load previously collected information from a
database.

The default mode, with no CLI options, run as an unprivileged user, is:

* Run in the foreground
* Do not switch to a different user
* Scan the music collection and write to results to a database
* Write access and error logs to the current console
* Rescan the music collection on ``SIGUSR1``

Running In The Foreground
=========================

With no options, the Avalon Music Server will run in the foreground. By default, the
access log will be written to ``STDOUT``. The error log will be written to ``STDERR``.

  ::

    avalonmsd ~/Music

Running As A Daemon
===================

When given the ``--daemon`` option, the Avalon Music server will become a well-behaved
UNIX daemon and run in the background. When running in daemon mode, the ``--access-log``
and ``--error-log`` options are required.

  ::

     avalonmsd --daemon --error-log /tmp/error.log \
         --access-log /tmp/access.log ~/Music


Running As A Daemon Started As Root
===================================

When run as root and given the ``--daemon-user`` and ``--daemon-group`` options (in
addition to the ``--daemon``, ``--access-log``, and ``--error-log`` options) the
Avalon Music Server will attempt to run as a different user and group. Before switching
to a different user and group it will attempt to change the ownership of the access log,
error log, and database file so that it will still be able to write to them.

  ::

    sudo avalonmsd --daemon --error-log /tmp/error.log \
        --access-log /tmp/access.log --daemon-user apache \
        --daemon-group apache ~/Music


In-Place Rescan
===============

The Avalon Music Server can be told to rescan a music collection and reload meta data
from the database while still running and serving requests. To do this send the server
a ``SIGUSR1`` using a program such as ``pkill`` or ``kill``.

  ::

    pkill -USR1 avalonmsd


Arguments
~~~~~~~~~

* ``collection`` - Path to the root of your music collection to scan

Options
~~~~~~~

* ``--access-log=PATH`` - Path to a file to use for logging requests to the server.

* ``--daemon`` - Fork into the background and run as a daemon.

* ``--daemon-user=USER`` - Run the server as this user. The server will switch to this non-privileged user when started as root and run in daemon mode.

* ``--daemon-group=GROUP`` - Run the server as this group. The server will switch to this non-privileged group when started as root and run in daemon mode.

* ``--db-path=PATH`` - Path to a file to use for the the backing SQLite database for storing collection meta data.

* ``--error-log=PATH`` - Path to a file to use for server errors and application informational logging.

* ``--no-scan`` - Do not rescan and rebuild the music collection at server start or during any reloads of the server (graceful events).

* ``--server-address=ADDR`` - Interface address to bind the server to. IPv4 and IPv6 addresses are supported. Default is localhost IPv4.

* ``--server-port=PORT`` - Port to listen for requests on. Default is port 8080.

* ``--server-queue=NUM`` - The number of incoming connections to the server to allow to be queued.

* ``--server-threads=NUM`` - The number of threads to use to process incoming requests for the server.

