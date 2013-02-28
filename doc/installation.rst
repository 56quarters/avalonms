Installation
------------

Prerequisites
~~~~~~~~~~~~~

Make sure you have the `pip Installer <http://www.pip-installer.org/>`_ and
`virtualenv <http://www.virtualenv.org/>`_ available. The ``virtualenv`` tool
is only needed if you do not have root permissions or don't wish to install
the Avalon Music Server globally.

You can install ``pip`` and ``virtualenv`` by running something like the
following:

Gentoo:

  :: 

    emerge dev-python/pip dev-python/virtualenv

Ubuntu/Mint/Debian

  ::

    apt-get install python-pip python-virtualenv


Installation via pip and PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. TODO: Change to be virtualenv install

To install the latest stable-ish version from PyPI:

  ::

    virtualenv ~/avalon
    source ~/avalon/bin/activate
    pip install avalonms


Installation from source
~~~~~~~~~~~~~~~~~~~~~~~~

To checkout and build the Avalon Music Server you'll need
`Git <http://git-scm.com/>`_ installed and a copy of the
`YUI build tool <http://yuilibrary.com/download/>`_ (in addition to ``pip``
and ``virtualenv``).

  ::

    virtualenv ~/avalon
    source ~/avalon/bin/activate
    git clone https://github.com/tshlabs/avalonms.git ~/avalon-src
    cd ~/avalon-src
    python setup.py version
    python setup.py static --yui-jar /path/to/yui.jar
    pip install -r requires.txt
    pip install .

