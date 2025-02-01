## Run Django
```poetry run python manage.py runserver```

## run tailwinf
```poetry run python manage.py tailwind start```



# Installation 

`poetry install`
`poetry run python manage.py makemigrations`

`poetry run python manage.py migrate`

# Load Example Data

1) `poetry run python manage.py add_users`

Mac, Linux:

2) `poetry run python manage.py loaddata data/activity/master-data/*.json`
2) `poetry run python manage.py loaddata data/activity/test-data/*.json`
3) `poetry run python manage.py loaddata data/food/*.json`
4) `poetry run python manage.py loaddata data/blog/*.json`

Windows:

2) `poetry run python manage.py add_fixtures data\activity\master-data\`
Run Server
`poetry run python manage.py runserver`


If statics are not already in sttic folder run this:
`poetry run python manage.py collectstatic`


# env file
in folder /config you need to put the .env file.
Next to the file settings.py

the file need to look like the example.env file in that folder


# login gcp database
`export USE_CLOUD_SQL_AUTH_PROXY=true`
`./cloud-sql-proxy inspi-441320:europe-west3:inspi-prod`

# deploy
`gcloud app deploy`

# requirment.txt
`poetry export --without-hashes --format=requirements.txt > requirements.txt`


# formater for template files
`poetry run djlint . --reformat`

# linter for template files
`poetry run djlint . --lint`