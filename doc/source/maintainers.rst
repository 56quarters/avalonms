Maintainers
-----------

.. note::

    The intended audience for this section is the Avalon Music Server
    maintainers. If you are a user of the Avalon Music Server, you don't
    need worry about this.

These are the steps for releasing a new version of the Avalon Music Server.
The steps assume that all the changes you want to release have already been
merged to the ``master`` branch. The steps further assumed that you've run
all the unit tests and done some ad hoc testing of the changes.

Versioning
~~~~~~~~~~

.. TODO: This part on semver belongs somewhere else

The Avalon Music Server uses `semantic versioning`_ of the form ``major.minor.patch``.
All backwards incompatible changes after version ``1.0.0`` will increment the major
version number. All backwards incompatible changes prior to version ``1.0.0`` will
increment the minor version number.

Since this is a Python project, only the subset of the semantic versioning spec that
is compatible with `PEP-440`_ will be used.

The canonical version number for the Avalon Music Server is contained in the file
``avalon/__init__.py`` (relative to the project root). Increment this version number based
on the nature of the changes being included in this release.

Do not commit.

Change Log
~~~~~~~~~~

Update the :doc:`change log </changes>` to include all relevant changes since the
last release. Make sure to note which changes are backwards incompatible.

Update the date of the most recent version to today's date.

Commit the version number and change log updates.

Tagging
~~~~~~~

Create a new tag based on the new version of the Avalon Music Server.

.. code-block:: bash

    $ git tag avalonms-0.5.0

Push the committed changes and new tags.

.. code-block:: bash

    $ fab push push_tags

Building
~~~~~~~~

Clean the checkout before trying to build.

.. code-block:: bash

    $ fab clean

Build source and binary distributions and upload them.

.. code-block:: bash

    $ fab pypi

Update PyPI
~~~~~~~~~~~

If the package metadata has changed since the last release, login to
PyPI and update the description field or anything else that needs it.

https://pypi.python.org/pypi/avalonms

.. _semantic versioning: http://semver.org/
.. _PEP-440: https://www.python.org/dev/peps/pep-0440/

