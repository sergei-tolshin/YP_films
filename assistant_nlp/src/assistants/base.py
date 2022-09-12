import copy
import logging
from typing import Optional

from core.dialog.serialized_message import SerializedMessage
from core.dialog import Context, Response


logger = logging.getLogger(__name__)


class BaseAssistant:
    def make_context(self, message: dict, **kwargs) -> Context:
        raise NotImplementedError()

    def make_response(self, response: Response,
                      original_message=None, **kwargs):
        raise NotImplementedError()

    def serialize_context(self, context: Context, data=None, **kwargs
                          ) -> Optional[SerializedMessage]:
        if data is None:
            data = context.raw_message
        if context.request_id is not None:
            kwargs['request_id'] = context.request_id
        return SerializedMessage(
            text=context.message_text,
            user_id=context.user_id,
            from_user=True,
            data=data,
            source=context.source,
            session_id=context.session_id,
            **kwargs
        )

    def serialize_response(self, data, context: Context, response: Response,
                           **kwargs) -> Optional[SerializedMessage]:
        data = copy.deepcopy(data)
        if context.request_id is not None:
            kwargs['request_id'] = context.request_id
        if response.label:
            kwargs['label'] = response.label
        return SerializedMessage(
            text=response.text,
            user_id=context.user_id,
            from_user=False,
            data=data,
            source=context.source,
            session_id=context.session_id,
            **kwargs
        )

    def uses_native_state(self, context: Context) -> bool:
        return False

    def get_native_state(self, context: Context) -> Optional[dict]:
        return
