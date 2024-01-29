#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# How to automate createsuperuser on django
# https://stackoverflow.com/questions/6244382/how-to-automate-createsuperuser-on-django/59467533#59467533
# python manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.create_user('game@planetchallenge.com', 'game1986')"
python app/manage.py collectstatic --no-input
python app/manage.py migrate

python app/manage.py drop_test_database --no-input
python app/manage.py test