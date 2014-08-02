Usage
-----

avalon-echo-config
~~~~~~~~~~~~~~~~~~

Prints the contents of the default configuration for the Avalon Music Server
WSGI application to ``STDOUT``.

Useful for creating a configuration file for the server that can be customized
as described below.

Synopsis
^^^^^^^^

::

    avalon-echo-config [options]

Options
^^^^^^^

    ``-h`` ``--help``
        Prints how to invoke the command and supported options and exits.

    ``-V`` ``--version``
        Prints the installed version of the Avalon Music Server and exits.

Examples
^^^^^^^^

::

    avalon-echo-config > /var/www/avalon/local-settings.py

avalon-scan
~~~~~~~~~~~

Scan a music collection for meta data and insert it into a database.

Synopsis
^^^^^^^^

::

    avalon-scan [options] {music collection path}

Options
^^^^^^^

    ``-h`` ``--help``
        Prints how to invoke the command and supported options and exits.

    ``-V`` ``--version``
        Prints the installed version of the Avalon Music Server and exits.

    ``-d <URL>`` ``--database <URL>``
        Database URL connection string for the database to write music collection
        meta data to. If not specified the value from the configuration file will
        be used. The URL must be one supported by SQLAlchemy_.

    ``-q`` ``--quiet``
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

The Avalon WSGI application is meant to be run with a Python WSGI server such as
Gunicorn_.

The application will...

* Load music collection meta data from a database (as specified by the configuration
  files described below).
* Build structures that can be used to search and query a music collection.
* Begin serving HTTP requests with a JSON API.

Running
^^^^^^^

The main entry point for the Avalon Music Server WSGI application is the module
``avalon.app.wsgi`` -- the WSGI callable is the attribute ``application`` within
the module. An example of how to use this module and callable with Gunicorn (with
three worker processes) is below. ::

    gunicorn --preload --workers 3 avalon.app.wsgi:application

Note that we're using the ``--preload`` mode which will save us memory when using
multiple worker processes.

Configuration
^^^^^^^^^^^^^

The Avalon WSGI application uses an embedded default configuration file. Settings
in that file (described below) can be overridden with a custom configuration file
generated as below (assuming the Avalon Music Server has already been installed). ::

    avalon-echo-config > /var/www/avalon/local-settings.py

The file at ``/var/www/avalon/local-settings.py`` will be an exact copy of the default
configuration file. You can change the settings in this new copy and they will
override the default settings. Any settings you do not change (or remove from the
file) will use their default values.

After you have customized this file, you need to tell the Avalon WSGI application
to use this file. This is done by setting the value of the ``AVALON_CONFIG``
environmental variable to the path of this configuration file. An example (once
again, using Gunicorn) is below. ::

    gunicorn --env AVALON_CONFIG=/var/www/avalon/local-settings.py \
        --preload --workers 3 avalon.app.wsgi:application

Settings
^^^^^^^^

The following configuration settings are available to customize the behavior of
the Avalon WSGI application. Note that some settings available in the configuration
are not meant to be changed by end users and are hence omitted. The table below
describes the settings and how they are used.



.. tabularcolumns:: |l|l|

=================== ===============================================================
``DATABASE_URL``    URL that describes the type of database to connect to and the
                    credentials for connecting to it. The URL must be one
                    supported by SQLAlchemy_. Some example URLs are given below.

                    Connecting to a remote PostgreSQL server:

                    ``postgresql+psycopg2://user:password@server/database``

                    Connecting to a local SQLite database:

                    ``sqlite:////var/db/avalon.sqlite``
                    
``LOG_DATE_FORMAT`` Date format for timestamps in logging messages. The supported
                    tokens for this setting are described in the Python
                    documentation_.

``LOG_FORMAT``      Format for messages logged directly by the Avalon Music
                    Server. See the Python logging_ documentation for more
                    information.

``LOG_LEVEL``       How verbose should logging done by the Avalon WSGI application
                    be? By default, all messages ``INFO`` and higher are logging.
                    Available levels are ``DEBUG``, ``INFO``, ``WARN``, ``ERROR``,
                    and ``CRITICAL``. Setting this to a higher value means that
                    fewer messages will be logged, but you may miss some useful
                    messages.

``LOG_PATH``        Where should messages be logged to? By default all messages
                    are logged to the ``STDERR`` stream (the console). Typically,
                    these will be captured by the Supervisord daemon and end up
                    in a log file. If you would like to have the Avalon WSGI
                    application write to the file itself, set this to the path
                    of the file.

``SENTRY_DSN``      URL that describes how to log errors to a centralized 3rd party
                    error-logging service, Sentry_. Enabling this logging requires
                    supplying a Sentry DSN configuration string and installing the
                    Raven Sentry client_.
=================== ===============================================================

Database
^^^^^^^^

Architecture
^^^^^^^^^^^^

Deployment
^^^^^^^^^^


.. _SQLAlchemy: http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
.. _Gunicorn: http://gunicorn.org
.. _uWSGI: http://uwsgi-docs.readthedocs.org/en/latest/
.. _documentation: http://docs.python.org/2/library/time.html#time.strftime
.. _logging: http://docs.python.org/2/library/logging.html#logrecord-attributes
.. _Sentry: https://getsentry.com/welcome/
.. _client: https://pypi.python.org/pypi/raven