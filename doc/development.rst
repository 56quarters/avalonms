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
is only chosen to make the documentation consistent.

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

    source env/bin/activate
    pip install -r requirements.txt --use-mirrors
    pip install -r requirements-test.txt --use-mirrors

Install the checkout in "development mode" and leave the virtual environment

  ::

    pip install -e .
    deactivate

Running The Server
~~~~~~~~~~~~~~~~~~

To run your local development copy of the server, you will need to enter the virtual
environment where it and all dependencies are installed.

  ::

    source env/bin/activate

Start the server with the path to your music collection as the sole argument.

  ::

    avalonmsd ~/Music

You can find more detail documentation for running the server in the :doc:`usage`
section.

To stop the server hit ``CTRL-c`` or type ``killall avalonmsd`` in another console. After
stopping the server leave the virtual environment.

  ::

    deactivate

Running Tests
~~~~~~~~~~~~~

Running tests for the server locally makes use of `py.test <http://pytest.org/>`_. To run
it, you must enter the virtual environment that you set up earlier. This command will run
all tests contained in the ``test`` directory using a few predefined
`rules <http://pytest.org/latest/goodpractises.html#test-discovery>`_.

  ::

    source env/bin/activate
    py.test test
    deactivate

