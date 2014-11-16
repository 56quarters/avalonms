# Configuration for running the Avalon Music Server under Gunicorn
# http://docs.gunicorn.org

# Note that this configuration omits a bunch of features that Gunicorn
# has (such as running as a daemon, changing users, error and access
# logging) because it is designed to be used when running Gunicorn
# with supervisord and a separate public facing web server (such as
# Nginx).

# Bind the server to an address only accessible locally. We'll be
# running Nginx which will proxy to Gunicorn and act as the public-
# facing web server.
bind = 'localhost:8000'

# Use three workers in addition to the master process. Since the Avalon
# Music Server is largely CPU bound, you can increase the number of
# request that can be handled by increasing this number (up to a point!).
# The Gunicorn docs recommend 2N + 1 where N is the number of CPUs you
# have.
workers = 3

# Make sure to load the application only in the main process before
# spawning the worker processes. This will save us memory when using
# multiple worker processes since the OS will be be able to take advantage
# of copy-on-write optimizations.
preload_app = True
