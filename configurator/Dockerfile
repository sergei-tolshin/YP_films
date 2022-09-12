ARG WORK_DIR="/configurator"
FROM python:3.10-slim as python_base
ARG WORK_DIR
RUN groupadd -g "${USER_GID:-1000}" dockeruser && \
    useradd -r -u "${USER_GID:-1000}" -g dockeruser -s /bin/bash -d "${WORK_DIR}" dockeruser
WORKDIR $WORK_DIR
RUN pip install -U pip pipenv
RUN chown -R dockeruser:dockeruser $WORK_DIR
EXPOSE 8000/tcp

FROM python_base as dev
COPY --chown=dockeruser:dockeruser Pipfile.lock Pipfile ./
RUN pipenv install --deploy --system --ignore-pipfile
USER dockeruser

FROM dev as prod
COPY --chown=dockeruser:dockeruser . .
