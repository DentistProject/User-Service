import django
from django.db import connection
from psycopg2 import OperationalError


from django.core.management.base import BaseCommand
from django.db import connection


help = "Starts the Django development server and prints a message when the database is successfully connected."

def check_db_connect():
    print("Checking database connection...")
    # Check if the database is successfully connected
    if connection.ensure_connection():
        print("Database is successfully connected!")
    else:
        print("Database is not connected")
