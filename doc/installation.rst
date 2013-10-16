Installation
------------

Prerequisites
~~~~~~~~~~~~~

Make sure you have the `pip Installer <http://www.pip-installer.org/>`_ and
`virtualenv <http://www.virtualenv.org/>`_ available. You can install ``pip``
and ``virtualenv`` by running something like the following:

Gentoo:

  :: 

    emerge dev-python/pip dev-python/virtualenv

Ubuntu/Mint/Debian

  ::

    apt-get install python-pip python-virtualenv


Installation via pip and PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the latest stable-ish version from PyPI:

  ::

    virtualenv ~/avalon
    source ~/avalon/bin/activate
    pip install avalonms


Installation from source
~~~~~~~~~~~~~~~~~~~~~~~~

To checkout and build the Avalon Music Server you'll need
`Git <http://git-scm.com/>`_ installed (in addition to ``pip``
and ``virtualenv``).

  ::

    virtualenv ~/avalon
    source ~/avalon/bin/activate
    git clone https://github.com/tshlabs/avalonms.git ~/avalon-src
    cd ~/avalon-src
    python setup.py version
    pip install -r requirements.txt
    pip install .

