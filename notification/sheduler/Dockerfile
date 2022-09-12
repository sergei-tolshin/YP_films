FROM python:3.10-slim
RUN apt-get update && apt-get -y install cron vim
RUN pip install -U pip pipenv
COPY Pipfile.lock Pipfile ./
RUN pipenv install --deploy --system --dev --ignore-pipfile
WORKDIR /app
COPY ./src /app
COPY crontab /etc/cron.d/crontab
RUN chmod 0744 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab
CMD ["cron", "-f"]



