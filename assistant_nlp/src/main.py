import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import alice, marusya, sber
from core import logger as logger_config

logger = logging.getLogger(__name__)

app = FastAPI(
    title='Webhook голосового помощника',
    description=('webhook'),
    version='1.0.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    redoc_url='/api/redoc',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    pass


@app.on_event('shutdown')
async def shutdown():
    pass


# Пока работает только Яндекс Алиса
app.include_router(alice.router, prefix='/api/v1/alice',
                   tags=['Голосовой помощник Алиса'])

app.include_router(marusya.router, prefix='/api/v1/marusya',
                   tags=['Голосовой помощник Маруся'])
app.include_router(sber.router, prefix='/api/v1/sber',
                   tags=['Голосовой помощник Салют.Сбер'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=3001,
        log_config=logger_config.LOGGING,
        log_level=logging.DEBUG,
    )
