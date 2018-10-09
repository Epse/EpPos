FROM python:3.5-onbuild
WORKDIR /usr/src/app
RUN mkdir -p db
RUN python manage.py migrate
