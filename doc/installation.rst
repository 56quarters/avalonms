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

To install the latest stable-ish version from PyPI:

  ::

    pip install avalonms


Installation via pip from source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the latest bleeding edge version from source:

  ::

    pip install -e git+https://github.com/tshlabs/avalonms.git#egg=avalonms


Manual installation
~~~~~~~~~~~~~~~~~~~

You'll need to ensure you have each of the dependencies listed in :doc:`requirements`
if you choose to install without using pip.

  ::

    # Download from http://pypi.python.org/pypi/avalonms

    tar -xzf avalonms-$version.tar.gz

    cd avalonms-$version

    python setup.py install
