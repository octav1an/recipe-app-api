FROM python:3.9-alpine3.13
LABEL maintainer="Octavian Catlabuga"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./src /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
  /py/bin/pip install --upgrade pip && \
  # OS deps needed to run the app
  apk add --update --no-cache postgresql-client jpeg-dev && \
  # Build deps are installed in a named virtual env that later is discarded
  apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev zlib zlib-dev && \ 
  /py/bin/pip install -r /tmp/requirements.txt && \
  if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt; \
  fi && \
  rm -rf /tmp && \
  apk del .tmp-build-deps && \
  adduser \
    --disabled-password \
    --no-create-home \
    django-user && \
  # Create the media directories
  mkdir -p /vol/web/media && \
  mkdir -p /vol/web/static && \
  # Change the owner so django app can access the files
  chown -R django-user:django-user /vol && \
  chmod -R 755 /vol

ENV PATH="/py/bin:$PATH"

USER django-user