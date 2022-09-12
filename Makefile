include .env

default:
	@echo init-env: destroy all containers, remove all named volumes and local images, recreate .env file
	@echo init-db-schema: load db schema to postgres database
	@echo load-test-data: load etalon test data to postgres database
	@echo admin-superuser: interactive create superuser for admin panel
	@echo test-rest: start functional test for movies rest api
	@echo update-openapi-schema: download and place to test data actual opanapi schema form movies rest api
	@echo ugc-api: up confluent kafka and ugc api

check_confirm:
	@( read -p "Are you sure? [y/N]: " sure && case "$$sure" in [yY]) true;; *) false;; esac )

init_warning:
	@echo "WARNING!!! it's delete all containers and data volumes"

update_schema_warning:
	@echo "WARNING!!! it's update test data!"


init-env: init_warning check_confirm
	docker-compose down -v --rmi local
	docker-compose -f rest/docker-compose.yml down -v --rmi local
	python3 configurator/misc/init_env.py
	cp .env rest/.env
	@echo export PYLINTRC=${PWD}/rest/.pylintrc >> rest/.env
	cp .env etl/.env
	@echo export PYLINTRC=${PWD}/etl/.pylintrc >> etl/.env
	cp .env admin_panel/.env
	@echo export PYLINTRC=${PWD}/admin_panel/.pylintrc >> admin_panel/.env
	cp .env auth/.env
	@echo export PYLINTRC=${PWD}/auth/.pylintrc >> auth/.env
	@echo export FLASK_APP=src/app.py >> auth/.env
	@echo export FLASK_ENV=development >> auth/.env
	cp .env ugc_api/.env

init-db-schema:
	docker-compose up -d movies-db
	docker-compose exec movies-db /root/wait-for-it.sh localhost:5432 -- psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /root/db_schema.sql

load-test-data:
	docker-compose build movies-configurator
	docker-compose run --rm movies-configurator  python test_data/load_data.py

admin-superuser:
	docker-compose up -d movies-admin-panel && docker-compose exec movies-admin-panel ./manage.py createsuperuser


update-openapi-etalon: update_schema_warning check_confirm
	docker-compose up -d --build nginx
	sleep 1
	curl http://localhost/api/openapi.json -o rest/test/functional/testdata/openapi.json

test-rest:
	docker-compose -f rest/docker-compose.yml up --build  movies-test \
	&& docker-compose -f rest/docker-compose.yml rm -sf movies-rest-test movies-redis-test elastic-test movies-test

ugc-api:
	docker-compose -f confluent/docker-compose.yml up -d
	docker-compose up -d ugc-rest
	docker-compose -f etl_kafka/docker-compose.yml up -d

ugc-api-2:
	docker-compose -f confluent/docker-compose.yml up -d
	docker-compose -f ugc_api/docker-compose.yml up -d
	@sleep 5
	./ugc_api/create_claster.sh
	docker-compose up -d auth-db auth-redis auth-rest ugc-rest elasticsearch-logs logstash nginx

notifications:
	docker-compose up -d auth-db auth-redis auth-rest rabbitmq notification_db notification_api notification_scheduler notification_workers

run.dev:
	docker-compose -f docker-compose.yml \
	-f docker-compose.override.yml \
	-f confluent/docker-compose.yml \
	-f etl_kafka/docker-compose.yml up


run.dev.silent:
	docker-compose -f docker-compose.yml \
	-f docker-compose.override.yml \
	-f confluent/docker-compose.yml \
	-f etl_kafka/docker-compose.yml up -d

build:
	docker-compose -f docker-compose.yml \
	-f docker-compose.override.yml \
	-f confluent/docker-compose.yml \
	-f etl_kafka/docker-compose.yml up --build

down:
	docker-compose -f docker-compose.yml \
	-f confluent/docker-compose.yml \
	-f etl_kafka/docker-compose.yml down

run.notification:
	docker-compose up --build rabbitmq notification_workers notification_db notification_email_sender \
	 admin_notification_api notification_scheduler notification_api auth-rest auth-db nginx

