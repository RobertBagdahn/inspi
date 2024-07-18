## Run Django
```poetry run python manage.py runserver```

## run tailwinf
```npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch```

# Create Virtual Environment

`virtualenv venv`

# Activate Virtual Environment

Mac, Linux:

`source venv/bin/activate`

Windows

`venv\Scripts\activate`

# Installation 

`pip install -r requirements.txt`

`python manage.py makemigrations`

`python manage.py migrate`

# Load Example Data

1) `python manage.py add_users`
2) `python manage.py add_keycloak_users`
3) `python manage.py sync_keycloak_groups`

Mac, Linux:

2) `python manage.py loaddata data/activity/master-data/*.json`
3) `python manage.py loaddata data/food/*.json`

Windows:

2) `python manage.py add_fixtures data\main\`
3) `python manage.py add_fixtures data\test\`
4) `python manage.py add_fixtures data\food-init\`

Run Server

`python manage.py runserver`

# deactivate venv

`deactivate`

# Dumpdata

Contenttypes: 

`python -Xutf8 manage.py dumpdata contenttypes.contenttype -o data\main\0_contenTypes.json`

Descriptions:

`python -Xutf8 manage.py dumpdata basic.description -o data\main\0_contenTypes.json`

Basic: 

`python -Xutf8 manage.py dumpdata basic --exclude=basic.IssueType --exclude=basic.ZipCode --exclude=basic.description --exclude=basic.ScoutOrgaLevel --exclude=basic.ScoutHierarchy -o data\test\1_completeBasic.json`

Email: 

`python -Xutf8 manage.py dumpdata email_services -o data\test\2_completeEmail.json`

Event: 

`python -Xutf8 manage.py dumpdata event -o data\test\3_completeEvent.json`
