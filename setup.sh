#!/bin/bash

# Install dependencies
poetry install

# Make migrations
poetry run python manage.py makemigrations

# Apply migrations
poetry run python manage.py migrate

# Load example data
poetry run python manage.py add_users

# Load data for Mac and Linux
poetry run python manage.py loaddata data/activity/master-data/*.json
poetry run python manage.py loaddata data/activity/test-data/*.json
poetry run python manage.py loaddata data/food/*.json
poetry run python manage.py loaddata data/blog/*.json
poetry run python manage.py loaddata data/masterdata/*.json
