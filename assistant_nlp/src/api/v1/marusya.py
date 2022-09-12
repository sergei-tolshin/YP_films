import logging

from fastapi import APIRouter, Depends, Request, status
from services.connector import (SOURCES, AssistantConnector,
                                get_assistant_connector_service)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/webhook',
             summary='Маруся',
             description='VK',
             status_code=status.HTTP_200_OK)
async def webhook(
    request: Request,
    assistant_connector: AssistantConnector = Depends(
        get_assistant_connector_service),
):
    req = await request.json()

    logger.debug('Receiving a message from Marusia: {}'.format(req))
    response = await assistant_connector.respond(req, source=SOURCES.MARUSYA)
    logger.debug('Sending a message to Marusa: {}'.format(response))

    return response
