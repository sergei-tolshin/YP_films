# YP_movies

Командный дипломный проект для Яндекс Практикум


## Настройка и запуск приложения и внешних сервисов:

* `touch .env && make init-env` - полностью удалить старые контейнеры, именованные тома контейнеров, локально собранные
  образа, пересоздать файл `.env`.
* `make init-db-schema` - поднять контейнер БД, загрузить структуру БД.
* `docker-compose up -d movies-etl` - поднять контейнер с ETL
* `docker-compose up -d nginx` - поднять контейнеры с `admin-panel`, `rest`, `auth` и `nginx`.
* `docker-compose up -d auth-jaeger` - поднять контейнеры с `jaeger`.
* (опционально) `make load-test-data` - загрузить в БД данные о фильмах, жанрах, персонале
* (опционально) `make admin-superuser` - добавить в админку админа.
* (опционально) `docker-compose up -d kibana` - поднять сервис kibana, доступен на http://127.0.0.1:5601 .
* (опционально)
  `cd auth`
  `pip install pipenv`
  `pipenv install --dev`
  `pipenv shell`
  `python -m flask users create-superuser` - добавить в `auth` админа.
* поставить ngrok (Запуск ./ngrok http http://localhost:3001)
* Создать навык алисы в Яндекс.Диалоге

## После запуска:

http://127.0.0.1/admin - админка
http://127.0.0.1/api/openapi - swagger-ui приложения

http://127.0.0.1:16686/ - jaeger-ui

