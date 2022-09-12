import os

PROJECT_NAME = os.getenv("PROJECT_NAME", "ugc_api")

TARGET_ENV = os.getenv("TARGET_ENV", "DEBUG")

RELOAD_ON_CHANGE = TARGET_ENV == "DEBUG"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

KAFKA_SEND_DELAY = 5
KAFKA_HOST = os.getenv("KAFKA_HOST", "localhost")
KAFKA_PORT = os.getenv("KAFKA_PORT", "9092")

GRPC_CHANNEL_HOST = os.getenv("GRPC_CHANNEL_HOST", "localhost")
GRPC_CHANNEL_PORT = os.getenv("GRPC_CHANNEL_PORT", "50055")

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))

SENTRY_DSN = os.getenv("SENTRY_DSN_UGC", "")
