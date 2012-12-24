Installation
------------

Prerequisites
~~~~~~~~~~~~~

Make sure you have the `pip Installer <http://www.pip-installer.org>`_ available.

You can install it by running something like the following:

Gentoo:

  :: 

    emerge dev-python/pip

Ubuntu/Mint/Debian

  ::

    apt-get install python-pip


Installation via pip and PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  ::

    pip install avalonms


Manual installation
~~~~~~~~~~~~~~~~~~~

You'll need to ensure you have each of the dependencies listed in :doc:`requirements`
if you choose to install without using pip and PyPI.

  ::

    # Download from http://pypi.python.org/pypi/avalonms

    tar -xzf avalonms-$version.tar.gz

    cd avalonms-$version

    python setup.py install
