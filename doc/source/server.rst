WSGI Application
----------------

The Avalon WSGI application is meant to be run with a Python WSGI server such as
Gunicorn_.

The application will...

* Load music collection meta data from a database (as specified by the configuration
  files described below).
* Build structures that can be used to search and query a music collection.
* Begin serving HTTP requests with a JSON :doc:`API </api>`.

Running
^^^^^^^

The main entry point for the Avalon Music Server WSGI application is the module
``avalon.app.wsgi`` -- the WSGI callable is the attribute ``application`` within
the module. An example of how to use this module and callable with Gunicorn (with
three worker processes) is below.

.. code-block:: bash

    $ gunicorn --preload --workers 3 avalon.app.wsgi:application

Note that we're using the ``--preload`` mode which will save us memory when using
multiple worker processes.

Configuration
^^^^^^^^^^^^^

The Avalon WSGI application uses an embedded default configuration file. Settings
in that file (described below) can be overridden with a custom configuration file
generated as below (assuming the Avalon Music Server has already been installed).

.. code-block:: bash

    $ avalon-echo-config > /var/www/avalon/local-settings.py

The file at ``/var/www/avalon/local-settings.py`` will be an exact copy of the default
configuration file. You can change the settings in this new copy and they will
override the default settings. Any settings you do not change (or settings removed from
the file) will use their default values.

After you have customized this file, you need to tell the Avalon WSGI application
to use this file. This is done by setting the value of the ``AVALON_CONFIG``
environmental variable to the path of this configuration file. An example (once
again, using Gunicorn) is below.

.. code-block:: bash

    $ gunicorn --env AVALON_CONFIG=/var/www/avalon/local-settings.py \
        --preload --workers 3 avalon.app.wsgi:application

Settings
^^^^^^^^

The following configuration settings are available to customize the behavior of
the Avalon WSGI application. The table below describes the settings and how they
are used.

.. note::

    Note that some settings available in the configuration are not meant to be changed
    by end users and are hence omitted below.

.. tabularcolumns:: |l|l|

=================== ===============================================================
``DATABASE_URL``    URL that describes the type of database to connect to and the
                    credentials for connecting to it. The URL must be one
                    supported by SQLAlchemy_. For example, to connect to a local
                    SQLite database: ``sqlite:////var/db/avalon.sqlite``, or to
                    connect to a remote PostgreSQL database:
                    ``postgresql+psycopg2://user:password@server/database``

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
                    error-logging service, Sentry_. This functionality is disabled
                    by default. Enabling this logging requires supplying a Sentry
                    DSN configuration string and installing the Raven `Sentry client`_.

``STATSD_HOST``     Hostname to write Statsd timers and counters to if there is a
                    client installed. The expected client will discard any errors
                    encountered when trying to write metrics so setting this value
                    to a host not running the Statsd daemon is equivalent to
                    disabling it.

``STATSD_PORT``     Port to write Statsd timers and counters to. Port 8125 is the
                    port that the Etsy Statsd implementation runs on by default.

``STATSD_PREFIX``   Prefix all metrics emitted with this string. Useful to make
                    sure metrics from the Avalon Music Server don't pollute the
                    top-level namespace. You may want further split metrics by
                    the environment you are running in (dev vs staging vs prod).
                    This can be done by adding a dot-separated string to the
                    existing prefix, e.g. 'avalon.prd' or 'avalon.dev'.
=================== ===============================================================

Architecture
^^^^^^^^^^^^

Database
========

The Avalon Music Server CLI tool ``avalon-scan`` writes music metadata to a database
when it scans a music collection. The WSGI application and reads the meta back when it
starts.

In each case, when connecting to a database for the first time, the CLI script and
the WSGI application will attempt to create the required database schema if it does
not already exist.

Provided that you attempt to scan your music collection before running the WSGI
application, the scanning portion must have read/write access to the database and
the WSGI application must have read access. Otherwise, if you are running the WSGI
application, connecting to a database before inserting anything into it via scanning,
the WSGI application will attempt create the required schema and will require read/write
access.

Workers
=======

The Avalon WSGI application is, for the most part, CPU bound and immutable after start
up. Therefore it is a good fit for multiprocess workers and (if your Python implementation
doesn't have a Global-Interpreter-Lock_) threaded workers.

Logging
=======

By default, the Avalon WSGI application sends logging messages to ``STDERR``. This means
that if you want to send these messages to a file or a Syslog, you have to configure the
logging of the WSGI HTTP server that you are using to run it (or the process manager that
runs the WSGI HTTP server).

The Avalon WSGI application can also be configured to send log messages directly to a log
file. In this case, the file must be writable by the user that the application is being
run as.

Sentry
======

Sentry_ is a centralized, 3rd-party, error-logging service. It is available as a
paid, hosted, service. However, both the client and server are `Free Software`_ and
can be run by anyone.

The Avalon WSGI application will optionally log unhandled exceptions to a Sentry
instance provided these things are true (otherwise logging to Sentry will not be
used).

#. The `Sentry client`_ is installed and can be imported.
#. There is a ``SENTRY_DSN`` configuration setting available and correctly configured.

To install the client run the following command from within the virtualenv that
the Avalon WSGI application is installed in.

.. code-block:: bash

    $ pip install raven

Statsd
======

Statsd_ is a daemon that listens for metrics sent over UDP and periodically pushes
them to Graphite_.

The Avalon WSGI application will optionally record the execution time of each endpoint
if the `Statsd client`_ is installed. The Statsd service to send metrics to can be
configured with the ``STATSD_HOST`` and ``STATSD_PORT`` configuration settings.

To install the client run the following command from within the virtualenv that
the Avalon WSGI application is installed in.

.. code-block:: bash

    $ pip install statsd

Deployment
^^^^^^^^^^

If you followed the steps in :doc:`installation` you should be able to use the
bundled Fabric_ deploy scripts to manage your Avalon WSGI application installation.

Note that the Fabric deploy scripts will also install the Gunicorn_ HTTP server and
a client for the Sentry_ service (however, Sentry won't be used unless you have
explicitly configured it).

Some assumptions made by the Fabric deploy scripts:

* You have already created and set the permissions of the directory that will be
  getting deployed to (as described in installation).
* You have SSH access to the server you are deploying to.
* You have the ability to ``sudo`` on the server you are deploying to.

If all these things are true, you should be able to deploy a new version of the
Avalon WSGI application with a few simple steps.

First, make sure the build environment is clean and then generate packages to install.

.. code-block:: bash

    $ fab clean build.released

Next, upload the generated packages, and install them.

.. code-block:: bash

    $ fab -H api.example.com deploy.install

Restart the Avalon WSGI application if it's already running.

.. code-block:: bash

    $ fab -H api.example.com deploy.restart

That's it! The Avalon WSGI application should now be running on your server.

.. _SQLAlchemy: http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
.. _Gunicorn: http://gunicorn.org
.. _uWSGI: http://uwsgi-docs.readthedocs.org/en/latest/
.. _documentation: http://docs.python.org/2/library/time.html#time.strftime
.. _logging: http://docs.python.org/2/library/logging.html#logrecord-attributes
.. _Sentry: https://getsentry.com/welcome/
.. _Sentry client: https://pypi.python.org/pypi/raven
.. _Global-Interpreter-Lock: https://wiki.python.org/moin/GlobalInterpreterLock
.. _Free Software: https://github.com/getsentry/sentry
.. _Fabric: http://www.fabfile.org/
.. _Statsd: https://codeascraft.com/2011/02/15/measure-anything-measure-everything/
.. _Statsd client: https://github.com/jsocol/pystatsd
.. _Graphite: http://graphite.readthedocs.org/en/latest/