#!/bin/sh
python manage.py migrate --fake v1 zero
python manage.py migrate
