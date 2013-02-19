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

.. TODO: Change to be virtualenv install

To install the latest stable-ish version from PyPI:

  ::

    pip install avalonms


.. TODO: Install from source with pip in a virtual env + yui


Manual installation
~~~~~~~~~~~~~~~~~~~

You'll need to ensure you have each of the dependencies listed in :doc:`requirements`
if you choose to install without using pip.

  ::

    # Download from http://pypi.python.org/pypi/avalonms

    tar -xzf avalonms-$version.tar.gz

    cd avalonms-$version

    python setup.py install
