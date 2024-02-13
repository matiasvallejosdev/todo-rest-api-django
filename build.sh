pip install -r requirements.txt

python3.9 manage.py collectstatic --no-input
python3.9 manage.py migrate

python3.9 manage.py drop_test_database --noinput
python3.9 manage.py test