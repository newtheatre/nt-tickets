#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # get the project dir
cd $dir   # cd into it
gunicorn wsgi:application --settings "settings"  # run gunicorn (default port)