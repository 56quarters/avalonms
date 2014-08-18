Development
-----------

Prerequisites
~~~~~~~~~~~~~

Make sure you have the `virtualenv <http://www.virtualenv.org/>`_ tool available.
You can find further instructions in the :doc:`installation` section or at the
virtualenv website.

All steps below assume you are using a virtual environment named ``env`` inside
the root directory of the git checkout. It's not important what name you use, this
is only chosen to make the documentation consistent. Most of the commands below
reference the ``pip``, ``virtualenv``, and ``python`` instances installed in
the ``env`` environment. This ensures that they run in the context of the
environment where we've set up the Avalon Music Server.

Environment Setup
~~~~~~~~~~~~~~~~~

First, `fork <https://help.github.com/articles/fork-a-repo>`_ the Avalon Music
Server on GitHub.

Check out your fork of the source code. ::

    git clone https://github.com/you/avalonms.git

Create and set up a branch for your awesome new feature or bug fix. ::

    cd avalonms
    git checkout -b feature-xyz
    git push origin feature-xyz:feature-xyz
    git branch -u origin/feature-xyz

Set up a virtual environment ::

    virtualenv env

Enter the virtualenv install required dependencies ::

    source env/bin/activate
    pip install --allow-external argparse -r requirements.txt
    pip install -r requirements-dev.txt
    pip install -r requirements-prod.txt

Install the checkout in "development mode" ::

    pip install -e .

Running The Server
~~~~~~~~~~~~~~~~~~

The Avalon Music Server WSGI application can be run using the builtin Flask
development server or it can be run with Gunicorn (which was installed above
from the ``requirements-prod.txt`` file). Make sure that you have entered the
virtualenv you created earlier.

Running with the development server: ::

    python -m avalon.app.wsgi

Or, run with Gunicorn: ::

    gunicorn --preload avalon.app.wsgi:application

Running Tests
~~~~~~~~~~~~~

The Avalon Music Server uses `tox <https://testrun.org/tox/latest/>`_ to run tests
in isolated virtualenvs. You can run the tests using the command below. Make sure
that you have entered the virtualenv you created earlier. ::

    tox test
