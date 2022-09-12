#!/usr/bin/env python

import logging

import uvicorn
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse

from api import router as api_router
from core import config, logger
from db import elastic, redis

ROUTERS = (api_router,)


def prepare_app(routers: tuple[APIRouter]) -> FastAPI:
    """init app, app routes, middlewares etc."""
    app_ = FastAPI(
        title=config.PROJECT_NAME,
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
    )
    for router in routers:
        app_.include_router(router)
    return app_


app = prepare_app(ROUTERS)


@app.on_event("startup")
async def startup():
    """startup hook"""
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.elastic = AsyncElasticsearch(
        hosts=[f"http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"]
    )


@app.on_event("shutdown")
async def shutdown():
    """shutdown hook"""
    await redis.redis.close()
    await elastic.elastic.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.RELOAD_ON_CHANGE,
        log_config=logger.LOGGING,
        log_level=logging.DEBUG,
    )
