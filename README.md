# recipe-app-api

Recipe API project.

## Other

Run linting

```
docker-compose run --rm app sh -c "flake8"
```

Run tests

```
docker-compose run --rm app sh -c "python manage.py test"
```

Add new django project

```
docker-compose run --rm app sh -c "django-admin startproject app ."
```
