#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# How to automate createsuperuser on django
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@todo.com').delete(); User.objects.create_user(email='matiasvallejosdev@outlook.com', password='19573')"

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py drop_test_database --noinput
python manage.py test