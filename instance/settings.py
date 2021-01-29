from os import environ

DATABASE = environ.get('DATABASE')
SECRET_KEY = environ.get('SECRET_KEY')
APP_ROUTE = environ.get('APP_ROUTE')