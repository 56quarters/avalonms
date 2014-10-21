Requirements
------------

If you follow the instructions in :doc:`installation` (using pip) most of
these requirements should be installed for you.

Python requirements:

* Python >= 2.6
* Argparse >= 1.2.1 (Or Python 2.7)
* Flask >= 0.10.1
* Mutagen >= 1.25.1
* SimpleJSON >= 3.5.2
* SQLAlchemy >= 0.9.4

In addition to the libraries above, you'll need a WSGI compatible server to
run the Avalon Music Server. Gunicorn_ or uWSGI_ are both excellent choices.
The rest of the documentation will assume you are using Gunicorn since that
is what the reference install of the Avalon Music Server uses.

By default, the Avalon Music Server uses a SQLite database to store music
meta data. If you wish to use another database type supported_ by SQLAlchemy
(e.g. MySQL, PostgreSQL) you'll need to install an appropriate library for
it.

For example, to install a PostgreSQL driver: ::

    pip install psycopg2

Or a MySQL driver: ::

    pip install mysql-python



.. _Gunicorn: http://gunicorn.org
.. _uWSGI: http://uwsgi-docs.readthedocs.org/en/latest/
.. _supported: http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls