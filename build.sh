#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python app/manage.py collectstatic --no-input
python app/manage.py migrate