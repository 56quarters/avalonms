#!/bin/bash

# Sample deploy [bash-only]script to install the Avalon Music server into virtual
# environments using pip and PyPI. The script does not need to be run as root,
# however, the user running it must have write permissions for $DEPLOY_ROOT. Virtual
# environments are created based on the current timestamp ("YYYYMMDDHHMMSS"). The
# symlink named "current" is updated to point at the most recent virtual environment
# deploy. All but the most recent five releases will be removed after each deploy.
# The script requires that the user running it has write permission to the /var/www/avalon
# directory. The server is not restarted after the deploy, this must be done separately.

# Number of deploys to keep, including the latest one
DEPLOYS_TO_KEEP=5

# Where virtual environments should be deployed to
DEPLOY_ROOT=/var/www/avalon

# The name of the deployment to create
DEPLOY_VERSION=`date +'%Y%m%d%H%M%S'`

# Temporary name for the current deployment while it is being built
DEPLOY_TMP_VERSION=`echo ${RANDOM} | md5sum | awk -F' ' '{ print $1 }'`

cd $DEPLOY_ROOT

echo "Installing avalonms in new virtualenv..."
virtualenv $DEPLOY_VERSION >/dev/null
source $DEPLOY_VERSION/bin/activate
pip install --use-mirrors avalonms >/dev/null
deactivate

echo "Setting $DEPLOY_VERSION to 'current'..."
ln -s $DEPLOY_VERSION $DEPLOY_TMP_VERSION
mv -T $DEPLOY_TMP_VERSION current

OLDEST_DEPLOYS=`ls -1v | grep -v 'current' | head -n -${DEPLOYS_TO_KEEP}`

if [ -n "$OLDEST_DEPLOYS" ]; then
    echo "Removing old deploys $OLDEST_DEPLOYS..."
    rm -rf $OLDEST_DEPLOYS
fi
