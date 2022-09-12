#!/bin/bash

./manage.py migrate --fake movies 0001_initial \
&& ./manage.py migrate \
&& ./manage.py collectstatic --noinput \
&& gunicorn config.wsgi
