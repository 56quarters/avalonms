Development
-----------

Prerequisites
~~~~~~~~~~~~~

Make sure you have the `pip Installer <http://www.pip-installer.org/>`_ and
`virtualenv <http://www.virtualenv.org/>`_ available. You can find further
instructions in the :doc:`installation` section or at the websites for each
respective tool.

All steps below assume you are using a virtual environment named ``env`` inside
the root directory of the git checkout. It's not important what name you use, this
is only chosen to make the documentation consistent. Most of the commands below
reference the ``pip``, ``virtualenv``, and ``python`` instances installed in
the ``env`` environment. This ensures that they run in the context of the
environment where we've set up the Avalon Music Server.

Environment Setup
~~~~~~~~~~~~~~~~~


Grab a copy of the source code

  ::

    git clone https://github.com/tshlabs/avalonms.git

Set up a virtual environment

  ::

    cd avalonms
    virtualenv env

Install required dependencies

  ::

    ./env/bin/pip install -r requirements2.txt --use-mirrors
    ./env/bin/pip install -r requirements-test2.txt --use-mirrors

Install the checkout in "development mode"

  ::

    ./env/bin/pip install -e .

Running The Server
~~~~~~~~~~~~~~~~~~

Start the server with the path to your music collection as the sole argument.

  ::

    ./env/bin/avalonmsd ~/Music

You can find more detail documentation for running the server in the :doc:`usage`
section.

To stop the server hit ``CTRL-c`` or type ``killall avalonmsd`` in another console.


Running Tests
~~~~~~~~~~~~~

Running tests for the server locally makes use of `py.test <http://pytest.org/>`_.  This
command will run all tests contained in the ``test`` directory using a few predefined
`rules <http://pytest.org/latest/goodpractises.html#test-discovery>`_.

  ::

    ./env/bin/py.test test

