Installation
------------

Two possible ways to install the Avalon Music Server are described below.
One is very simple and designed to get you up and running as quickly as
possible. The other is more involved and designed to run the Avalon Music
Server in a production environment.

All of these instructions are based on a machine running Debian Linux, but
they should be applicable to any UNIX-like operating system (with a few
modifications).

.. note::

    The ``$`` character at the beginning of each of the commands listed below
    just indicates the start of the command prompt, don't actually enter this
    in your terminal!

Quick Start Installation
~~~~~~~~~~~~~~~~~~~~~~~~

This section will describe an extremely simple installation of the Avalon
Music Server. If you just want to play around with the Avalon Music Server
and don't have plans to run it in production, this guide is for you.

First, we'll install the virtualenv tool.

.. code-block:: bash

    $ apt-get install python-virtualenv

Next, create a virtual environment that we'll install the Avalon Music Server into.

.. code-block:: bash

    $ virtualenv ~/avalon

"Activate" the virtual environment.

.. code-block:: bash

    $ source ~/avalon/bin/activate

Install the Avalon Music Server and Gunicorn_.

.. code-block:: bash

    $ pip install avalonms gunicorn

Scan your music collection and build a database with the meta data from it.

.. code-block:: bash

    $ avalon-scan ~/path/to/music

Start the server.

.. code-block:: bash

    $ gunicorn --preload avalon.app.wsgi:application

Then, in a different terminal, test it out!

.. code-block:: bash

    $ curl http://localhost:8000/avalon/heartbeat

You should see the result ``OKOKOK`` if the server started correctly. To stop
the server, just hit ``CTRL-C`` in the terminal that it is running in.

Production Installation
~~~~~~~~~~~~~~~~~~~~~~~

This section will describe one potential way to install, configure, and
run the Avalon Music Server in production. The configuration described is
very similar to how the reference installation of the Avalon Music Server
(http://api.tshlabs.org/avalon/version) is set up.

This particular installation uses Gunicorn_, Supervisord_, and Nginx_. We'll
set it up so that it can be deployed to using the included Fabric_ files in
the future. We'll also make use of the bundled Gunicorn and Supervisor
configurations.


Installing Dependencies
=======================

First, we'll install the virtualenv tool, Supervisor and Nginx using the package
manager.

.. code-block:: bash

    $ apt-get install python-virtualenv supervisor nginx

Setting Up The Environment
==========================

Next, we'll set up the environment on our server:

Create the group that will own the deployed code.

.. code-block:: bash

    $ sudo groupadd dev

Add our user to it so that we can perform deploys without using sudo.

.. code-block:: bash

    $ sudo usermod -g dev `whoami`

Create the directories that the server will be deployed into.

.. code-block:: bash

    $ sudo mkdir -p /var/www/avalon/releases

Set the ownership and permissions of the directories.

.. code-block:: bash

    $ sudo chown -R root:dev /var/www/avalon
    $ sudo chmod -R u+rw,g+rw,o+r /var/www/avalon
    $ sudo chmod g+s /var/www/avalon /var/www/avalon/releases

Add a new unprivileged user that the Avalon Music Server will run as.

.. code-block:: bash

    $ sudo useradd --shell /bin/false --home /var/www/avalon --user-group avalon

Create a virtual environment that we'll install the Avalon Music Server into.

.. code-block:: bash

    $ virtualenv /var/www/avalon/releases/20140717214022

Set the "current" symlink to the virtual environment we just created. This is
the path that we'll we pointing our Supervisor and Gunicorn configurations at.

.. code-block:: bash

    $ ln -s /var/www/avalon/releases/20140717214022 /var/www/avalon/current

Installing from PyPI
====================

Now, let's install the Avalon Music Server, Gunicorn, and a Sentry client into
the virtual environment we just created.

.. code-block:: bash

    $ /var/www/avalon/current/bin/pip install avalonms gunicorn raven

The Avalon Music Server has an embedded default configuration file. In addition
to that, we'll create our own copy of that configuration that we can customize.

.. code-block:: bash

    $ /var/www/avalon/current/bin/avalon-echo-config > /var/www/avalon/local-settings.py

Avalon WSGI Application
=======================

We won't configure the Avalon WSGI application here, as part of installation. For
more information about the available configuration settings for it, see the :doc:`usage`
section.

Gunicorn
========

The installed Avalon Music Server comes with a simple Gunicorn configuration file
that is available at ``/var/www/avalon/current/share/avalonms/avalon-gunicorn.py``
(or ``ext/avalon-gunicorn.py`` in the codebase). This file configures Gunicorn to:

* Bind the server to only the local interface, port ``8000``.
* Spawn three worker processes that will handle requests.
* Use preload mode so that the workers will be able to take advantage of copy-on-write_
  optimizations done by the operating system to save RAM.

Supervisor
==========

The installed Avalon Music server also comes with a simple Supervisord configuration
file. This file runs the Avalon Music Server as an unprivileged user, uses the Gunicorn
HTTP WSGI server, restarts it if it crashes, and pipes all output to a log file. This
is available at ``/var/www/avalon/current/share/avalonms/avalon-supervisor-gunicorn.conf``
(or ``ext/avalon-supervisor-gunicorn.conf`` in the codebase).

When you installed Supervisor earlier (if you're on Debian) it created a directory that
configurations can be placed into: ``/etc/supervisor/conf.d``. Copy the bundled Supervisor
configuration file into this directory and set the owner and permissions appropriately.

.. code-block:: bash

    $ cp /var/www/avalon/current/share/avalonms/avalon-supervisor-gunicorn.conf /etc/supervisor/conf.d/
    $ chown root:root /etc/supervisor/conf.d/avalon-supervisor-gunicorn.conf
    $ chmod 644 /etc/supervisor/conf.d/avalon-supervisor-gunicorn.conf

Nginx
=====

Though Gunicorn can run as an HTTP server, you should_ use a dedicated web server in front
of it as a reverse proxy if you plan on exposing it on the public Internet. If so, Nginx is
a solid, lightweight, easy to configure choice. In the instructions below, replace
``api.example.com`` with the domain that you wish to run the Avalon Music Server at.

When you installed Nginx earlier it created a directory that server configurations can be
placed into: ``/etc/nginx/sites-available/`` (if you're on Debian). If you're not on Debian
the directory may be in a different location such as ``/etc/nginx/conf.d`` or you may have
a single configuration file: ``/etc/nginx/nginx.conf``.

If you have a directory for configurations, create a new file named ``api_example_com.conf``
with the contents below. If you only have a single configuration file, add the contents below
inside the ``http`` section. ::

    upstream avalon {
             server localhost:8000;
    }

    server {
       listen 80;
       server_name api.example.com;

       location /avalon {
                proxy_pass http://avalon;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
       }
    }

If you're on Debian, enable the configuration like so.

.. code-block:: bash

    $ sudo ln -s /etc/nginx/sites-available/api_example_com.conf /etc/nginx/sites-enabled/

Start the Server
================

Now that everything is configured, let's try starting Nginx and Supervisor (which will, in turn,
start the Avalon Music Server) and testing it out.

.. code-block:: bash

    $ sudo service supervisor start
    $ sudo service nginx start
    $ curl http://api.example.com/avalon/heartbeat

If everything was installed correctly, the ``curl`` command should return the string
``OKOKOK``.

.. _Gunicorn: http://www.gunicorn.org/
.. _should: http://docs.gunicorn.org/en/latest/deploy.html
.. _Supervisord: http://www.supervisord.org/
.. _Nginx: http://nginx.org/
.. _Fabric: http://www.fabfile.org/
.. _copy-on-write: https://en.wikipedia.org/wiki/Copy-on-write#Copy-on-write_in_virtual_memory_management
