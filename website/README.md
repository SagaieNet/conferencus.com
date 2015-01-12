# Flask based web application

## Running the application

    source venv/bin/activate
    ./manage.py

## Running the admin application

    source venv/bin/activate
    ./manage.py admin

## Running the worker

    celery -A website.tasks worker --loglevel=info

## Setting up database schema

Run this from python interactive shell

    from website import *
    db.create_all()