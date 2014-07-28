Usage
-----

avalon-echo-config
~~~~~~~~~~~~~~~~~~

Prints the contents of the default configuration for the Avalon Music Server
WSGI application to ``STDOUT``.

Synopsis
^^^^^^^^

::

    avalon-echo-config [options]

Options
^^^^^^^

    -h --help
        Prints how to invoke the command and supported options and exits.

    -V --version
        Prints the installed version of the Avalon Music Server and exits.

Examples
^^^^^^^^

::

    avalon-echo-config > /etc/avalon/local-config.py

avalon-scan
~~~~~~~~~~~

Scan a music collection for meta data and insert it into a database.

Synopsis
^^^^^^^^

::

    avalon-scan [options] {music collection path}

Options
^^^^^^^

    -h --help
        Prints how to invoke the command and supported options and exits.

    -V --version
        Prints the installed version of the Avalon Music Server and exits.

    -d <URL> --database <URL>
        Database URL connection string for the database to write music collection
        meta data to. If not specified the value from the configuration file will
        be used. The URL must be one supported by SQLAlchemy_.

    -q --quiet
        Be less verbose, only emit ERROR level messages to the console.

Examples
^^^^^^^^

Use the default database type (SQLite) and location (usually /tmp/avalon.sqlite)
and scan the music collection in the directory 'music'. ::

    avalon-scan ~/music

Use a PostgreSQL database type and connect to a remote database server and
scan the music collection in the directory 'music'. ::

    avalon-scan --database 'postgresql+psycopg2://user:password@server/database' ~/music

Use a SQLite database type in a non-default location and scan the music collection
in the directory '/home/files/music'. ::

    avalon-scan --database 'sqlite:////var/db/avalon.sqlite' /home/files/music

Avalon WSGI App
~~~~~~~~~~~~~~~

Description
^^^^^^^^^^^

Configuration
^^^^^^^^^^^^^

Settings
^^^^^^^^

Database
^^^^^^^^

Architecture
^^^^^^^^^^^^

Deployment
^^^^^^^^^^


.. _SQLAlchemy: http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls