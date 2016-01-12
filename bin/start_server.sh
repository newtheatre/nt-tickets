# Starts the production server for nt-tickets
# access to this server is proxied through NGINX

# sets the address and the bind port for the applications

ADDRESS=127.0.0.1
PORT=8002

DJANGO_SETTINGS_MODULE="settings"
GUNICORN_ARGS="--settings $DJANGO_SETTINGS_MODULE --bind $ADDRESS:$PORT"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # get the bin dir
cd $DIR/..   # cd into the one above, ie the project
gunicorn wsgi:application $GUNICORN_ARGS  # run gunicorn (default port)