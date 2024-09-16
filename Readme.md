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
3) `poetry run python manage.py add_fixtures data\activity\test-data\`
4) `poetry run python manage.py add_fixtures data\food\`
4) `poetry run python manage.py add_fixtures data\blog\`

Run Server

`poetry run python manage.py runserver`


# env file
in folder /inspiApp you need to put the .env file.
Next to the file settings.py

the file need to look like the example.env file in that folder

Windows users have to put this line in settings.py:
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"