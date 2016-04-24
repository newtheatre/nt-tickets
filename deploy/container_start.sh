#!/bin/sh
cd /var/projects/tickets && python manage.py migrate --noinput
supervisord -n -c /etc/supervisor/supervisord.conf