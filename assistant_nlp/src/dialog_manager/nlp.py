import logging
from functools import lru_cache

from core.dialog import Context, Response
from core.dialog.names import COMMANDS
from fastapi import Depends
from services.dialogflow import DialogFlow, get_dialogflow_service
from services.handlers import Handlers

from .base import BaseDialogManager


class NLPDialogManager(BaseDialogManager):
    def __init__(self, nlp_client, *args, **kwargs):
        super(NLPDialogManager, self).__init__(*args, **kwargs)
        self.nlp_client = nlp_client

    async def respond(self, ctx: Context):
        commands = []
        suggests = []
        uo = ctx.user_object

        if 'session' not in uo:
            uo['session'] = {}

        try:
            if ctx.session_is_new():
                response = await self.nlp_client.event('Welcome',
                                                       ctx.session_id)
            else:
                response = await self.nlp_client.message(ctx.message_text,
                                                         ctx.session_id)

            handlers = Handlers(response, uo)
            import time
            time.sleep(1)

            if response.action == 'goodbye':
                text = response.text
                suggests = response.suggests
                commands.append(COMMANDS.EXIT)
            elif (response.action == 'welcome' or
                  response.action == 'help' or
                  response.action == 'unknown'):
                text = response.text
                suggests = response.suggests
            elif handler_action := getattr(handlers, response.action):
                uo, text, suggests = await handler_action()
        except Exception as error:
            logging.error('Error!', exc_info=error)
            text = ('Похоже в видеомагнитофоне зажевало пленку.\n'
                    'Скоро мы все починим.')

        return Response(
            user_object=uo,
            text=text,
            suggests=suggests,
            commands=commands
        )


@lru_cache()
def get_nlp_dialog_manager(
    nlp_client: DialogFlow = Depends(get_dialogflow_service)
) -> NLPDialogManager:
    return NLPDialogManager(nlp_client=nlp_client)
