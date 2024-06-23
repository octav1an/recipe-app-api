# recipe-app-api

Recipe API project.

## Other

Run linting

```
docker compose run --rm app sh -c "flake8"
```

Run tests

```
docker compose run --rm app sh -c "python manage.py test"
```

Add new django project

```
docker compose run --rm app sh -c "django-admin startproject app ."
```

Add new django app

```
docker compose run --rm app sh -c "python manage.py startapp [name]"
```

Create superuser

```
docker compose run --rm app sh -c "python manage.py createsuperuser"
```

Admin page: `http://localhost:8000/admin/`
API docs: `http://localhost:8000/api/docs/`

### Authentication

In order to use swagger you have to authenticate.

1. Get token `/api/user/token/` using user and pass
2. In swagger chose _tokenAuth_ and set: `Token <token>` and authorize
