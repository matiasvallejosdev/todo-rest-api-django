pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py drop_test_database --noinput
python manage.py test