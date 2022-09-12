#!/bin/bash
cd src
python services/grc_server.py &
gunicorn "app:create_app()" -b 0.0.0.0:5000
