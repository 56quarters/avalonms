#!/bin/sh

# Sample init script to start, stop, or reload the Avalon music server based
# on the variables defined below. The script is expected to be run as root
# so that it has permission to switch to a different user (and possibly bind
# to the requested port to list to requests on). The script is extremely simple
# and assumes there will only ever be a single server instance running at a time.
# The script uses /var/tmp for log files and the database file by default. It starts
# the server and attempts to run it as the apache user (and group). The server
# is started with in 'no scan' mode so it will only read from the database. This 
# means the database file must be generated ahead of time.

# Full path to the current version of the server executable
AMS_BIN=/var/www/avalon/current/bin/avalonmsd

# Base name of the server executable
AMS_EXEC=`basename ${AMS_BIN}`

# Path to the SQLite database that should be used
PATH_DB=/var/tmp/avalon/avalon.sqlite

# Path to the error log file
PATH_ERR=/var/tmp/avalon/avalon.err

# Path to the access log file
PATH_LOG=/var/tmp/avalon/avalon.log

# User and group to switch to
DAEMON_USER=apache
DAEMON_GROUP=apache

# How long we'll wait for the server to start before exiting with non-zero status
TIMEOUT_START=10

# How long we'll wait for the server to stop before using SIGKILL and exiting with
# non-zero status
TIMEOUT_STOP=15


is_running() {
    pgrep -x "${AMS_EXEC}" > /dev/null
    if [ 0 = $? ]; then
        echo 'yes'
    else
        echo 'no'
    fi
}


start() {
    if [ 'yes' = `is_running` ]; then
        echo "${AMS_EXEC} appears to already be running!" 1>&2
        return 1
    fi

    "${AMS_BIN}" --daemon --daemon-user "${DAEMON_USER}" --daemon-group "${DAEMON_GROUP}" \
        --db-path "${PATH_DB}" --access-log "${PATH_LOG}" --error-log "${PATH_ERR}" \
        --no-scan /dev/null

    local i=0
    while [ 'no' = `is_running` ] && [ $i -lt $TIMEOUT_START ]; do
        i=$(($i + 1))
        sleep 1
    done

    if [ 'yes' = `is_running` ]; then
        return 0
    fi

    return 1
}


stop() {
    if [ 'no' = `is_running` ]; then
        echo "${AMS_EXEC} doesn't appear to be running!" 1>&2
        return 1
    fi

    pkill -TERM -x "${AMS_EXEC}" >/dev/null

    local i=0
    while [ 'yes' = `is_running` ] && [ $i -lt $TIMEOUT_STOP ]; do
        i=$(($i + 1))
        sleep 1
    done

    if [ 'no' = `is_running` ]; then
        return 0
    fi

    pkill -KILL -x "${AMS_EXEC}" >/dev/null
    return 1    
}


case "$1" in
    status)
        status
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    reload)
        pkill -USR1 -x "${AMS_EXEC}" >/dev/null
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|reload}"
        exit 1
esac

