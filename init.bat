rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser --username alex@acooper.org --email alex@acooper.org
python dummy_data.py
