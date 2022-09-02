#!/bin/sh

python manage.py migrate --no-input

python manage.py collectstatic --no-input

python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME  \
        --email $DJANGO_SUPERUSER_EMAIL

daphne -b 0.0.0.0 -p 8000 EfwBuilder.asgi:application