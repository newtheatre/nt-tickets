# Installing nt-tickets

## Prerequisites
You will need:

- Python (and virtualenv, because it's very sensible)
- A web server to proxy nt-tickets through, probably NGNIX or Apache
- Packages for the imaging library we use (Pillow, a 'friendly' fork of the PIL)
    - Some of these: python-dev libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms1-dev libwebp-dev

## To Install

- Pop your database details into configuration/development.py staging.py or production.py
- Change configuration/enviroment.py to match what enviroment you'd like to use
- pip install -r requirements.txt (google any compilation errors, usually you're just missing a package, or two)
- python manage.py syncdb, create yourself a superuser
- python manage.py migrate
- bin/start.sh, you can modify this file to change the default port (8000)

## To Configure

The file configuration/customise.py will exist soon and allow you to quickly customise nt-tickets to your organisation. This feature still needs to be implemented.

## Test the web interface
Once nt-tickets is up and running connect locally to port 8000 (or whatever it's set to in bin/start.sh). You should get a generic index page. Now try logging into the admin area at /manage. If all goes OK you've configured nt-tickets correctly.

## Configure you web server
Configuration of your web server is a little beyond the scope of this document. See the following pages for tips:

- http://gunicorn.org/#deployment
- http://www.apachetutor.org/admin/reverseproxies

For production you will need to serve static and media files using your web server and not django/nt-tickets. In the nt-tickets directory /static should be mapped to http://your-url/static and /media to http://your-url/media.
