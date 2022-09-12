import logging

import kafka
from fastapi import Depends, Request, Header, status, HTTPException
from motor import motor_asyncio

import core.grpc.userpb2 as user_pb2
import core.grpc.userpb2grpc as user_pb2_grpc
from core.config import PROJECT_NAME

PRODUCER: kafka.KafkaProducer | None = None
VIEW_STUB: user_pb2_grpc.UserStub | None = None
GRPC_CHANNEL = None
MONGO_CLIENT = None


def get_producer() -> kafka.KafkaProducer | None:
    return PRODUCER


def get_grpc_client() -> user_pb2_grpc.UserStub | None:
    return VIEW_STUB


def get_mongo_client() -> motor_asyncio.AsyncIOMotorClient | None:
    return MONGO_CLIENT


async def check_token(
        access_token: str | None = Header(default=None),
        grpc_=Depends(get_grpc_client)
):
    """
    Get username from valid token.

    :param access_token: jwt access token.
    :param grpc_: grpc client.
    """
    if not access_token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Access token is required.")
    auth_response = await grpc_.GetName(user_pb2.UserViewRequest(access_token=access_token))
    return auth_response


def add_extra_fields_in_logger_record(request: Request):
    logger_ = logging.getLogger(PROJECT_NAME)
    logger_ = logging.LoggerAdapter(logger_, dict(request_id=request.headers.get("X-Request-Id"), url=request.url))
    return logger_
