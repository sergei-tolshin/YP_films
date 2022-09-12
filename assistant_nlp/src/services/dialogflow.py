import os
from functools import lru_cache

from core.config import settings
from google.api_core.exceptions import InvalidArgument
from google.cloud import dialogflow_v2
from google.protobuf.json_format import MessageToDict
from models.dialogflow import Dialogflow as DialogflowModel


class DialogFlow:
    def __init__(self) -> None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.dirname(
            os.path.abspath(__file__)) + '/keys/public_key.json'
        self.client = dialogflow_v2.SessionsAsyncClient

    async def message(self, text: str, session_id: str = 'me'):
        text_input = dialogflow_v2.TextInput(
            text=text,
            language_code=settings.DIALOGFLOW_LANGUAGE_CODE
        )
        query_input = dialogflow_v2.QueryInput(text=text_input)
        return await self.get_response(query_input, session_id)

    async def event(self, name: str, session_id: str = 'me'):
        event_input = dialogflow_v2.EventInput(
            name=name,
            language_code=settings.DIALOGFLOW_LANGUAGE_CODE
        )
        query_input = dialogflow_v2.QueryInput(event=event_input)
        return await self.get_response(query_input, session_id)

    async def get_response(self, query_input, session_id: str):
        async with self.client() as async_client:
            session = async_client.session_path(
                settings.DIALOGFLOW_PROJECT_ID,
                session_id
            )
            try:
                response = await async_client.detect_intent(
                    query_input=query_input,
                    session=session
                )
            except InvalidArgument:
                raise InvalidArgument
        response_dict = MessageToDict(response.query_result._pb)
        return DialogflowModel.from_dict(response_dict)


@lru_cache()
def get_dialogflow_service() -> DialogFlow:
    return DialogFlow()
