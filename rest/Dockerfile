ARG WORK_DIR=/rest

FROM python:3.10-slim AS python_base
ARG WORK_DIR
RUN groupadd -g "${USER_GID:-1000}" dockeruser && \
    useradd -r -u "${USER_GID:-1000}" -g dockeruser -s /bin/bash -d $WORK_DIR dockeruser
WORKDIR $WORK_DIR
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN pip install -U pip pipenv
RUN chown -R dockeruser:dockeruser $WORK_DIR
EXPOSE 8000/tcp

FROM python_base AS dev
COPY --chown=dockeruser:dockeruser Pipfile.lock Pipfile ./
RUN pipenv install --deploy --system --ignore-pipfile
USER dockeruser
EXPOSE 8000/tcp

FROM python_base AS test
COPY --chown=dockeruser:dockeruser Pipfile.lock Pipfile ./
RUN pipenv install --deploy --system --dev --ignore-pipfile
USER dockeruser
COPY --chown=dockeruser:dockeruser . .
ENTRYPOINT ["./test/functional/docker-entrypoint.sh"]

FROM dev AS prod
COPY --chown=dockeruser:dockeruser . .
ENTRYPOINT ["./docker-entrypoint.sh"]
