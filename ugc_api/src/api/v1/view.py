import logging

from core.services import get_producer, check_token, add_extra_fields_in_logger_record
from fastapi import APIRouter, status, Depends, HTTPException
from models.view import ViewRequest

router = APIRouter(prefix="/view", tags=["view"])

logger = logging.getLogger(__name__)

TOPIC = "movie_view_progress"


@router.post("/")
async def view_movie_create(
        request_data: ViewRequest,
        auth_response=Depends(check_token),
        producer=Depends(get_producer),
        logger_=Depends(add_extra_fields_in_logger_record)

):
    """Function add entry to Kafka."""

    if not auth_response.username:
        logger_.info("Token not valid.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token not valid.")
    producer.send(
        topic=TOPIC,
        value=request_data.movie_time,
        key="{username}+{movie_id}".format(username=auth_response.username, movie_id=request_data.movie_id)
    )
    return status.HTTP_200_OK
