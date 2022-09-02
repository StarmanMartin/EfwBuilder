#!/bin/sh

python manage.py migrate --noinput

python manage.py collectstatic --noinput

python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME  \
        --email $DJANGO_SUPERUSER_EMAIL

daphne -b 0.0.0.0 -p 8000 EfwBuilder.asgi:application