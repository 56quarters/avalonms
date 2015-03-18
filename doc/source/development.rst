Development
-----------

Prerequisites
~~~~~~~~~~~~~

Make sure you have the virtualenv_ tool available. You can find further instructions
in the :doc:`installation` section or at the virtualenv website.

All steps below assume you are using a virtual environment named ``env`` inside
the root directory of the git checkout. It's not important what name you use, this
is only chosen to make the documentation consistent. Most of the commands below
reference the ``pip``, ``virtualenv``, and ``python`` instances installed in
the ``env`` environment. This ensures that they run in the context of the
environment where we've set up the Avalon Music Server.

Environment Setup
~~~~~~~~~~~~~~~~~

First, fork_ the Avalon Music Server on GitHub.

Check out your fork of the source code.

.. code-block:: bash

    $ git clone https://github.com/you/avalonms.git

Add the canonical Avalon Music Server repo as ``upstream``. This might be
useful if you have to keep your branch / repo up to date before creating
a pull request.

.. code-block:: base

    $ git remote add upstream https://github.com/tshlabs/avalonms.git

Create and set up a branch for your awesome new feature or bug fix.

.. code-block:: bash

    $ cd avalonms
    $ git checkout -b feature-xyz
    $ git push origin feature-xyz:feature-xyz
    $ git branch -u origin/feature-xyz

Set up a virtual environment.

.. code-block:: bash

    $ virtualenv env

Enter the virtualenv install required dependencies.

.. code-block:: bash

    $ source env/bin/activate
    $ pip install --allow-external argparse -r requirements.txt
    $ pip install -r requirements-dev.txt
    $ pip install -r requirements-prod.txt

Install the checkout in "development mode".

.. code-block:: bash

    $ pip install -e .

Running The Server
~~~~~~~~~~~~~~~~~~

The Avalon Music Server WSGI application can be run using the builtin Flask
development server or it can be run with Gunicorn (which was installed above
from the ``requirements-prod.txt`` file). Make sure that you have entered the
virtualenv you created earlier.

Running with the development server:

.. code-block:: bash

    $ python -m avalon.app.wsgi

Or, run with Gunicorn:

.. code-block:: bash

    $ gunicorn --preload avalon.app.wsgi:application

Memory Profiling
~~~~~~~~~~~~~~~~

The Avalon Music Server WSGI application can optionally log the memory used by
various internal data structures. This can be useful for minimizing the resource
footprint of the server when adding new features.

When enabled, memory usage will be writen to the configured logger. This feature
is only enabled when the Pympler_ package is installed and the configured log
level is ``DEBUG``.

To enable this do the following.

Install the profiler.

.. code-block:: bash

    $ pip install pympler

Change the Avalon Music Server log level in your local ``settings.py`` file.

.. code-block:: python

    LOG_LEVEL = logging.DEBUG

Contributing
~~~~~~~~~~~~

Next, code up your feature or bug fix and create a `pull request`_. If you're new to
Git or GitHub, take a look at the `GitHub help`_ site.

Useful Commands
~~~~~~~~~~~~~~~

The Avalon Music Server uses tox_ to run tests in isolated virtualenvs. You can run
the tests using the command below. Make sure that you have entered the virtualenv
you created earlier.

.. code-block:: bash

    $ tox test

You can also run the unit tests for a specific Python version.

.. code-block:: bash

    $ TOXENV=py33 tox test

If you're making changes to the documentation, the command below will build the
documentation for you. To view it, open up ``doc/build/html/index.html`` in your
web browser.

.. code-block:: bash

    $ fab clean docs

.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _fork: https://help.github.com/articles/fork-a-repo
.. _pull request: https://help.github.com/articles/be-social/#pull-requests
.. _GitHub help: https://help.github.com/
.. _tox: https://testrun.org/tox/latest/
.. _Pympler: https://pypi.python.org/pypi/Pympler
