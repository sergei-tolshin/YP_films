import random
import string

PWD_LENGTH = 32


def gen_pwd():
    letters = string.ascii_letters
    digits = string.digits
    box = letters + digits

    return "".join(random.choice(box) for _ in range(PWD_LENGTH))


ENV_TEMPLATE = f"""
export USER_GID=1000
export DJANGO_SETTINGS_MODULE="config.settings"
export DJANGO_SECRET_KEY={gen_pwd()}
export POSTGRES_USER=mvadmin
export POSTGRES_DB=movies_database
export POSTGRES_PASSWORD={gen_pwd()}
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export ELASTIC_HOST=localhost
export ELASTIC_PORT=9200

export RTEST_REDIS__HOST=localhost
export RTEST_REDIS__PORT=6379
export RTEST_ELASTIC__HOST=localhost
export RTEST_ELASTIC__PORT=9200
export RTEST_REST__HOST=localhost
export RTEST_REST__PORT=8000

export REDIS_HOST=localhost
export REDIS_PORT=6379

export ELASTIC_HOST=localhost
export ELASTIC_PORT=9200

export AUTH_REST_HOST=localhost
export AUTH_REST_PORT=5001

export AUTH_REDIS_HOST=localhost
export AUTH_REDIS_PORT=6380

export AUTH_POSTGRES_USER=authadmin
export AUTH_POSTGRES_DB=auth_database
export AUTH_POSTGRES_PASSWORD={gen_pwd()}
export AUTH_POSTGRES_HOST=localhost
export AUTH_POSTGRES_PORT=5433

export AUTH_REDIS_TEST__HOST=localhost
export AUTH_REDIS_TEST__PORT=6380

export AUTH_POSTGRES_TEST__HOST=localhost
export AUTH_POSTGRES_TEST__PORT=5433
export AUTH_POSTGRES_TEST__USER=authadmin
export AUTH_POSTGRES_TEST__PASSWORD=$AUTH_POSTGRES_PASSWORD

export AUTH_AUTH_TEST__HOST=localhost
export AUTH_AUTH_TEST__PORT=5002

export KAFKA_HOST=broker
export KAFKA_PORT=29092

export GRPC_CHANNEL_HOST=auth-rest
export GRPC_CHANNEL_PORT=50055
"""


def main():
    with open(".env", "w", encoding="utf-8") as envfile:
        print(ENV_TEMPLATE.strip(), file=envfile)


if __name__ == '__main__':
    main()
