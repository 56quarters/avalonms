CLI Tools
---------

There are several CLI tools that are used as part of the Avalon Music Server
besides the actual server part.

Each of these tools will be detailed below.

avalon-echo-config
~~~~~~~~~~~~~~~~~~

Print the contents of the default configuration for the Avalon Music Server
WSGI application to ``STDOUT``.

Useful for creating a configuration file for the server that can be customized
as described below.

Synopsis
^^^^^^^^

.. code-block:: bash

    $ avalon-echo-config [options]

Options
^^^^^^^

    ``-h`` ``--help``
        Prints how to invoke the command and supported options and exits.

    ``-V`` ``--version``
        Prints the installed version of the Avalon Music Server and exits.

Examples
^^^^^^^^

.. code-block:: bash

    $ avalon-echo-config > /var/www/avalon/local-settings.py


avalon-scan
~~~~~~~~~~~

Scan a music collection for meta data and insert it into a database, making
sure to create the database schema if it does not already exist.

Database connection information is loaded from the default configuration file
and optionally a configuration override file (whose location is specified by
the ``AVALON_CONFIG`` environmental variable). This can also be overridden using
the ``--database`` option.

Synopsis
^^^^^^^^

.. code-block:: bash

    $ avalon-scan [options] {music collection path}

Options
^^^^^^^

    ``-h`` ``--help``
        Prints how to invoke the command and supported options and exits.

    ``-V`` ``--version``
        Prints the installed version of the Avalon Music Server and exits.

    ``-d <URL>`` ``--database <URL>``
        Database URL connection string for the database to write music collection
        meta data to. If not specified the value from the default configuration file
        and configuration file override will be used. The URL must be one supported
        by SQLAlchemy_.

    ``-q`` ``--quiet``
        Be less verbose, only emit ERROR level messages to the console.

Examples
^^^^^^^^

Use the database type and location specified by the default configuration
file (usually SQLite and ``/tmp/avalon.sqlite``) and scan the music collection
in the directory 'music'.

.. code-block:: bash

    $ avalon-scan ~/music

Use the database type and location specified by a custom configuration file
and scan the music collection in the 'media' directory.

.. code-block:: bash

    $ AVALON_CONFIG=/home/user/avalon/local-settings.py avalon-scan /home/media

Use a PostgreSQL database type and connect to a remote database server and
scan the music collection in the directory 'music'.

.. code-block:: bash

    $ avalon-scan --database 'postgresql+psycopg2://user:password@server/database' ~/music

Use a SQLite database type in a non-default location and scan the music collection
in the directory '/home/files/music'.

.. code-block:: bash

    $ avalon-scan --database 'sqlite:////var/db/avalon.sqlite' /home/files/music

.. _SQLAlchemy: http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls