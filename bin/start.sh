#!/bin/bash

# This scipt starts the gunicorn webserver for the nt-tickets application
# You need to be 'in' your virtual enviroment before running me

# This is the address and port that the gunicorn webserver will run on
# You don't want this publically accessable, rather you should proxy access
# to it via apache or ngnix
ADDRESS=127.0.0.1
PORT=8000

DJANGO_SETTINGS_MODULE="settings"
GUNICORN_ARGS="--settings $DJANGO_SETTINGS_MODULE --bind $ADDRESS:$PORT"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # get the bin dir
cd $DIR/..   # cd into the one above, ie the project
gunicorn wsgi:application $GUNICORN_ARGS  # run gunicorn (default port)