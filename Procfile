web:python manage.py runserver
web: gunicorn ticket.wsgi --log-file -
heroku ps:scale web=1