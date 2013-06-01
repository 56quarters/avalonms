Usage
-----

Running the server
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

Running in the foreground
=========================

With no options, the Avalon Music Server will run in the foreground. By default, the
access log will be written to ``STDOUT``. The error log will be written to ``STDERR``.

  ::

    avalonmsd ~/Music

Running as a daemon
===================

When given the ``--daemon`` option, the Avalon Music server will become a well-behaved
UNIX daemon and run in the background. When running in daemon mode, the ``--access-log``
and ``--error-log`` options are required.

  ::

     avalonmsd --daemon --error-log /tmp/error.log \
         --access-log /tmp/access.log ~/Music


Running as a daemon started as root
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


.. _running-on-a-public-interface:

Running on a public interface
=============================

By default the Avalon Music Server will bind to a local address (typically 127.0.0.1) and
will not be publicly accessible. If you want it to bind to a public address (and therefore
allow other people to connect to the server) you must use the ``--server-address`` option
to specify what address to use.

IPv4

  ::

    avalonmsd --server-address 0.0.0.0 ~/Music

IPv6

  ::

    avalonmsd --server-address :: ~/Music


Running behind an Apache reverse proxy
======================================

If you already run a public facing Apache HTTP server you can configure it to act as
a reverse proxy for a locally bound Avalon Music Server instance.

Start the Avalon Music Server with a command like the following:

  ::

    sudo avalonmsd --daemon --error-log /tmp/error.log \
        --access-log /tmp/access.log --daemon-user apache \
        --daemon-group apache ~/Music

And use an Apache virtual host configuration like the following:

  ::

    <VirtualHost *:80>
        ServerName api.tshlabs.org

        KeepAlive Off
        RewriteEngine Off

        SetOutPutFilter DEFLATE

        <Location "/">
          Order deny,allow
          Allow from all
        </Location>

        ProxyPass /avalon http://localhost:8080/avalon
        ProxyPassReverse /avalon http://localhost:8080/avalon
    </VirtualHost>


In-place rescan
===============

The Avalon Music Server can be told to rescan a music collection and reload metadata
from the database while still running and serving requests. To do this, send the server
the signal ``SIGUSR1`` using a program such as ``pkill`` or ``kill``. If the server was
started with the ``--no-scan`` option ``SIGUSR1`` will not cause it to rescan the music
collection, only reload information from the database.

  ::

    pkill -USR1 avalonmsd


Arguments
~~~~~~~~~

* ``collection`` - Path to the root of your music collection to scan. If you tell the server not to rescan your
  collection on start up this only needs to be a path that exists, for example you could use ``/dev/null``.

Options
~~~~~~~

* ``--access-log=PATH`` - Path to a file to use for logging requests to the server. This file must be writable by
  the user the server is running as. By default the access log will be written to ``STDOUT``.

* ``--daemon`` - Fork into the background and run as a daemon. The server will detach from the current console
  and run indefinitely until it recieves a ``SIGTERM`` signal. Enabling this option requires that you also specify
  the ``access-log`` and ``error-log`` options.

* ``--daemon-user=USER`` - Run the server as this user. The server will switch to this non-privileged user when
  started as root and run in daemon mode. The ownership of the access and error logs and the database file will
  be changed to this user.

* ``--daemon-group=GROUP`` - Run the server as this group. The server will switch to this non-privileged group when
  started as root and run in daemon mode. The ownership of the access and error logs and the database file will be
  changed to this group.

* ``--db-path=PATH`` - Path to a file to use for the the backing SQLite database for storing collection metadata.
  This file must be writable by the user the server is running as. By default the database file will be written
  to ``$TEMP/avalon.sqlite`` where ``$TEMP`` is determined per system at runtime (usually it's just ``/tmp``).

* ``--error-log=PATH`` - Path to a file to use for server errors and application informational logging. This file must
  be writable by the user the server is running as. By default the the error log will be written to ``STDERR``.

* ``--no-scan`` - Do not rescan and rebuild the music collection at server start or during any reloads of the server
  (graceful events). The music collection will still be loaded from the database at ``db-path`` and loaded into
  memory again during reloads of the server, however the database WILL NOT be written to. To be safe, you could
  change the permissions of the database file to read only.

* ``--server-address=ADDR`` - Interface address to bind the server to. IPv4 and IPv6 addresses are supported. Default
  is localhost IPv4. If you want people to be able to publicly access the server, you must change this to some to
  other value as mentioned above: :ref:`running-on-a-public-interface`.

* ``--server-port=PORT`` - Port to listen for requests on. Default is port 8080. Port numbers below 1024 require
  that the server be started as root.

* ``--server-queue=NUM`` - The number of incoming connections to the server to allow to be queued. The default number
  is four, the same as the number of threads to use for the server. I've found this to be a reasonable default, your
  mileage may vary.

* ``--server-threads=NUM`` - The number of threads to use to process incoming requests for the server. The default
  number is four. If you are using a Python implementation with a GIL (Global Interpreter Lock) increasing this value
  may not result in dramatically better throughput. Again, your mileage may vary.

