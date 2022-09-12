FROM python:3.10-slim

WORKDIR /code
COPY Pipfile.lock Pipfile ./
RUN pip install -U pip pipenv
RUN pipenv install --system
COPY . .
