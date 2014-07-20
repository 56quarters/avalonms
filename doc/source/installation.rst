Installation
------------

This section will describe one potential way to install, configure, and
run the Avalon Music Server in production. The configuration described is
very similar to how the reference installation of the Avalon Music Server
(http://api.tshlabs.org/avalon/version) is set up.

This particular installation uses Gunicorn_, Supervisord_, and Nginx_. We'll
set it up so that it can be deployed to using the included Fabric_ files in
the future. We'll also make use of the bundled Gunicorn and Supervisor
configurations.

These instructions are based on a machine running Debian Linux, but they
should be applicable to any UNIX-like operating system.

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

First, we'll install the virtualenv tool, Supervisor and Nginx using the package
manager. ::

    apt-get install python-virtualenv supervisor nginx

Setting Up The Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, we'll set up the environment on our server:

* Create the group that will own the deployed code. ::

    sudo groupadd dev

* Add our user to it so that we can perform deploys without using sudo. ::

    sudo usermod -g dev `whoami`

* Create the directories that the server will be deployed into. ::

    sudo mkdir -p /var/www/avalon/releases

* Set the ownership and permissions of the directories. ::

    sudo chown -R root:dev /var/www/avalon
    sudo chmod -R u+rw,g+rw,o+r /var/www/avalon
    sudo chmod g+s /var/www/avalon /var/www/avalon/releases

* Add a new unprivileged user that the Avalon Music Server will run as. ::

    sudo useradd --shell /bin/false --home /var/www/avalon --user-group avalon

* Create a virtualenv that we'll install the Avalon Music Server into. ::

    virtualenv /var/www/avalon/releases/20140717214022

* Set the "current" symlink to the virtualenv we just created. This is the
  path that we'll we pointing our Supervisor and Gunicorn configurations at. ::

    ln -s /var/www/avalon/releases/20140717214022 /var/www/avalon/current

Installing from PyPI
~~~~~~~~~~~~~~~~~~~~

Now, let's install the Avalon Music Server and Gunicorn into the virtualenv
we just created. ::

    /var/www/avalon/current/bin/pip install avalonms gunicorn

The Avalon Music Server has a embedded default configuration file. In addition
to that, we'll create our own copy of that configuration that we can customize. ::

    /var/www/avalon/current/bin/avalon-echo-config > /var/www/avalon/local-settings.py

Configure the Avalon WSGI Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

.. Installation? Deploy?
.. Setting up local configuration
.. Setting up env var for local configuration

.. DB setup?

.. Resource usage?

.. Logging?

Configure Gunicorn WSGI HTTP Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The installed Avalon Music Server comes with a simple Gunicorn configuration file
that is available at ``/var/www/avalon/current/share/avalonms/avalon-gunicorn.py``.
This file configures Gunicorn to:

* Bind the server to only the local interface, port ``8000``.
* Spawn three worker processes that will handle requests.
* Use preload mode so that the workers will be able to take advantage of copy-on-write_
  optimizations done by the operating system to save RAM.

Configure Supervisor Process Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The installed Avalon Music server also comes with a simple Supervisord configuration
file. This file runs the Avalon Music Server as an unprivileged user, uses the Gunicorn
HTTP WSGI server, restarts it if it crashes, and pipes all output to a log file. This
is available at ``/var/www/avalon/current/share/avalonms/avalon-supervisor-gunicorn.conf``.

When you installed Supervisor earlier (if you're on Debian) it created a directory that
configurations can be placed into: ``/etc/supervisor/conf.d``. Create a symlink in this
directory to the bundled Supervisor configuration file. ::

    ln -s /var/www/avalon/current/share/avalonms/avalon-supervisor-gunicorn.conf /etc/supervisor/conf.d/

Configure Nginx Web Server
~~~~~~~~~~~~~~~~~~~~~~~~~~

Though Gunicorn can run as an HTTP server, you should consider using a dedicated web server
in front of it as a reverse proxy if you plan on exposing it on the public Internet. If so,
Nginx is a solid, lightweight, easy to configure choice. In the instructions below, replace
``api.example.com`` with the domain that you wish to run the Avalon Music Server at.

When you installed Nginx earlier it created a directory that server configurations can be
placed into: ``/etc/nginx/sites-available/`` (if you're on Debian). If you're not on Debian
the directory may be in a different location or you may have a single configuration
file: ``/etc/nginx/nginx.conf``.

If you have a directory for configurations, create a new file named ``api_example_com.conf``
with the contents below. If you only have a single configuration file, add the contents below
under the ``http`` section. ::

    server {
       listen 80;
       server_name api.example.com;

       location /avalon {
                proxy_pass             http://127.0.0.1:8000;
                proxy_set_header       Host $host;
       }
    }

If you're on Debian, enable the configuration like so: ::

    sudo ln -s /etc/nginx/sites-available/api_example_com.conf /etc/nginx/sites-enabled/

Start the Server
~~~~~~~~~~~~~~~~

Now that everything is configured, let's try starting Nginx and Supervisor (which will, in turn,
start the Avalon Music Server) and testing it out. ::

    sudo service supervisor start
    sudo service nginx start
    curl http://api.example.com/avalon/heartbeat

If everything was installed correctly, the ``curl`` command should return the string
``OKOKOK``.

.. _Gunicorn: http://www.gunicorn.org/
.. _Supervisord: http://www.supervisord.org/
.. _Nginx: http://nginx.org/
.. _Fabric: http://www.fabfile.org/
.. _copy-on-write: https://en.wikipedia.org/wiki/Copy-on-write#Copy-on-write_in_virtual_memory_management