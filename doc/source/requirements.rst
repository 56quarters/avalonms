Requirements
------------

If you follow the instructions in :doc:`installation` (using pip) most of
these requirements should be installed for you.

Python requirements:

* Python >= 2.6
* Argparse >= 1.2.1 (Or Python 2.7)
* Flask >= 0.10.1
* Mutagenx >= 1.23
* SimpleJSON >= 3.5.2
* SQLAlchemy >= 0.9.4

In addition to the libraries above, you'll need a WSGI compatible server to
run the Avalon Music Server. `Gunicorn <http://gunicorn.org/>`_ or
`uWSGI <http://uwsgi-docs.readthedocs.org/en/latest/>`_ are both excellent
choices. The rest of the documentation will assume you are using Gunicorn
since that is what the reference install of the Avalon Music Server uses.
