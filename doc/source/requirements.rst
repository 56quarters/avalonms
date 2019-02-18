Requirements
------------

If you follow the instructions in :doc:`installation` (using pip) most of
these requirements should be installed for you.

Python requirements:

* Python 2 >= 2.7 or Python 3 >= 3.5
* Flask >= 1.0.2
* Mutagen >= 1.42.0
* SimpleJSON >= 3.16.0
* SQLAlchemy >= 1.2.18

In addition to the libraries above, you'll need a WSGI compatible server to
run the Avalon Music Server. Gunicorn_ or uWSGI_ are both excellent choices.
The rest of the documentation will assume you are using Gunicorn since that
is what the reference install of the Avalon Music Server uses.

By default, the Avalon Music Server uses a SQLite database to store music
meta data. If you wish to use another database type supported_ by SQLAlchemy
(e.g. MySQL, PostgreSQL) you'll need to install an appropriate library for
it.

For example, to install a PostgreSQL driver.

.. code-block:: bash

    $ pip install psycopg2

Or a MySQL driver.

.. code-block:: bash

    $ pip install mysql-python

.. _Gunicorn: http://gunicorn.org
.. _uWSGI: http://uwsgi-docs.readthedocs.org/en/latest/
.. _supported: http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
