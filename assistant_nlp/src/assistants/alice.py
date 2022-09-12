from typing import Optional

from .base import BaseAssistant, Context, Response, logger
from core.dialog.names import SOURCES, REQUEST_TYPES
from models.yandex import YandexRequest, YandexResponse
from core.utils.text import encode_uri


class AliceAssistant(BaseAssistant):
    SOURCE = SOURCES.ALICE

    def __init__(self, native_state: bool = False, **kwargs):
        super(AliceAssistant, self).__init__(**kwargs)
        self.native_state = native_state

    def make_context(self, message: dict, **kwargs) -> Context:
        metadata = {}

        if set(message.keys()) == {'body'}:
            message = message['body']
        try:
            sess = message['session']
        except KeyError:
            raise KeyError(
                f'Ключ "session" не найден {list(message.keys())}.')
        if sess.get('user', {}).get('user_id'):
            user_id = self.SOURCE + '_auth__' + sess['user']['user_id']
        else:
            user_id = self.SOURCE + '__' + sess['user_id']
        try:
            message_text = message['request'].get('command', '')
        except KeyError:
            raise KeyError(
                f'Ключ "request" не найден {list(message.keys())}.')
        metadata['new_session'] = message.get('session', {}).get('new', False)

        ctx = Context(
            user_object=None,
            message_text=message_text,
            metadata=metadata,
            user_id=user_id,
            session_id=sess.get('session_id'),
            source=self.SOURCE,
            raw_message=message,
        )

        ctx.request_type = message['request'].get(
            'type', REQUEST_TYPES.SIMPLE_UTTERANCE)
        ctx.payload = message['request'].get('payload', {})
        try:
            ctx.yandex = YandexRequest.from_dict(message)
        except Exception as e:
            logger.warning(
                'Не удалось десериализовать запрос Yandex: '
                'получено исключение "{}".'.format(e))

        return ctx

    def make_response(self, response: Response,
                      original_message: dict = None, **kwargs):
        result = {
            "version": original_message['version'],
            "response": {
                "end_session": response.has_exit_command,
                "text": response.text
            }
        }
        if self.native_state and response.updated_user_object:
            if self.native_state == 'session':
                result['session_state'] = response.updated_user_object
            elif self.native_state == 'application':
                result['application_state'] = response.updated_user_object
            elif self.native_state == 'user':
                if original_message.get('session') and \
                        'user' not in original_message['session']:
                    result['application_state'] = response.updated_user_object
                result['user_state_update'] = response.updated_user_object
            else:
                if 'session' in response.updated_user_object:
                    result['session_state'] = response.updated_user_object['session']
                if 'application' in response.updated_user_object:
                    result['application_state'] = response.updated_user_object['application']
                if 'user' in response.updated_user_object:
                    result['user_state_update'] = response.updated_user_object['user']
        if response.raw_response is not None:
            if isinstance(response.raw_response, YandexResponse):
                result = response.raw_response.to_dict()
            else:
                result['response'] = response.raw_response
            return result
        buttons = response.links or []
        for button in buttons:
            if 'url' in button:
                button['url'] = encode_uri(button['url'])
        if response.suggests:
            buttons = buttons + [{'title': suggest}
                                 for suggest in response.suggests]
        for button in buttons:
            if not isinstance(button.get('hide'), bool):
                button['hide'] = True
        result['response']['buttons'] = buttons
        return result

    def uses_native_state(self, context: Context) -> bool:
        return bool(self.native_state)

    def get_native_state(self, context: Context) -> Optional[dict]:
        if not self.native_state:
            return
        message = context.raw_message or {}
        state = message.get('state', {})

        if self.native_state == 'session':
            user_object = state.get('session')
        elif self.native_state == 'user':
            user_object = state.get('user')
            if message.get('session') and 'user' not in message['session']:
                user_object = state.get('application')
        elif self.native_state == 'application':
            user_object = state.get('application')
        else:
            user_object = state
        return user_object
