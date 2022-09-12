#!/usr/bin/env python

import logging
from logging import config as logging_config

import backoff
import grpc
import kafka
import sentry_sdk
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse
from kafka.errors import NoBrokersAvailable
from motor.motor_asyncio import AsyncIOMotorClient
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from api import router as api_router
from core import config, logger, services
from core.grpc.userpb2grpc import UserStub

ROUTERS = (api_router,)


def prepare_app(routers: tuple[APIRouter]) -> FastAPI:
    """Init app, app routes, middlewares etc."""
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        traces_sample_rate=1.0,
    )
    fastapi_app = FastAPI(
        title=config.PROJECT_NAME,
        docs_url="/ugc/api/openapi",
        openapi_url="/ugc/api/openapi.json",
        default_response_class=ORJSONResponse,
    )
    fastapi_app.add_middleware(SentryAsgiMiddleware)
    for router in routers:
        fastapi_app.include_router(router)
    return fastapi_app


app = prepare_app(ROUTERS)


@app.on_event("startup")
@backoff.on_exception(backoff.expo, NoBrokersAvailable)
async def startup() -> None:
    """Startup hook."""
    logger.LOGGING["root"]["level"] = config.LOG_LEVEL
    logging_config.dictConfig(logger.LOGGING)
    services.PRODUCER = kafka.KafkaProducer(
        bootstrap_servers=["{host}:{port}".format(host=config.KAFKA_HOST, port=config.KAFKA_PORT)],
        linger_ms=config.KAFKA_SEND_DELAY,
        key_serializer=lambda key: bytes(str(key), "utf-8"),
        value_serializer=lambda value: bytes(str(value), "utf-8"),
    )
    services.GRPC_CHANNEL = grpc.aio.insecure_channel(
        "{host}:{port}".format(
            host=config.GRPC_CHANNEL_HOST,
            port=config.GRPC_CHANNEL_PORT,
        ),
    )
    services.VIEW_STUB = UserStub(services.GRPC_CHANNEL)

    services.MONGO_CLIENT = AsyncIOMotorClient(config.MONGO_HOST, config.MONGO_PORT)


@app.on_event("shutdown")
async def shutdown() -> None:
    """Shutdown hook."""
    services.PRODUCER.close()
    await services.GRPC_CHANNEL.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.RELOAD_ON_CHANGE,
        log_config=logger.LOGGING,
        log_level=logging.DEBUG,
    )
