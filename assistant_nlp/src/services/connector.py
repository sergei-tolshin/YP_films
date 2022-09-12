import copy
from functools import lru_cache
from typing import Any, Optional

from assistants import (AliceAssistant, BaseAssistant, MarusyaAssistant,
                        SberAssistant)
from core.dialog import Context, Response
from core.dialog.names import SOURCES
from fastapi import Depends

from dialog_manager.base import BaseDialogManager
from dialog_manager.nlp import NLPDialogManager, get_nlp_dialog_manager


class AssistantConnector:
    def __init__(
            self,
            dialog_manager: BaseDialogManager,
            storage=None,
            default_source: str = SOURCES.ALICE,
            alice_native_state: bool = False,
            assistants: Optional[dict[str, BaseAssistant]] = None,
    ):
        self.dialog_manager = dialog_manager
        self.default_source = default_source
        self.storage = storage
        self.alice_native_state = alice_native_state
        self.assistants: dict[str, BaseAssistant] = assistants or {}
        self._add_default_assistants()

    def _add_default_assistants(self):
        if SOURCES.ALICE not in self.assistants:
            self.assistants[SOURCES.ALICE] = AliceAssistant(
                native_state=self.alice_native_state
            )
        if SOURCES.MARUSYA not in self.assistants:
            self.assistants[SOURCES.MARUSYA] = MarusyaAssistant()
        if SOURCES.SBER not in self.assistants:
            self.assistants[SOURCES.SBER] = SberAssistant()

    async def add_assistant(self, name: str, assistant: BaseAssistant):
        self.assistants[name] = assistant

    async def respond(self, message: dict, source: str = None) -> Any:
        ctx, resp, result = await self.full_respond(message=message,
                                                    source=source)
        return result

    async def full_respond(self, message: dict, source: str = None
                           ) -> tuple[Context, Response, Any]:
        context = await self.make_context(message=message, source=source)
        return await self.respond_to_context(context=context)

    async def respond_to_context(self, context: Context
                                 ) -> tuple[Context, Response, Any]:
        source = context.source
        assistant = self.assistants.get(source)
        old_user_object = copy.deepcopy(context.user_object)

        response = await self.dialog_manager.respond(context)
        if response.updated_user_object is not None \
                and response.updated_user_object != old_user_object:
            if assistant and assistant.uses_native_state(context=context):
                pass
            else:
                await self.set_user_object(context.user_id,
                                           response.updated_user_object)

        result = await self.standardize_output(
            source=source,
            original_message=context.raw_message,
            response=response
        )

        return context, response, result

    async def make_context(self, message: dict, source: str = None):
        if source is None:
            source = self.default_source
        assert source in self.assistants, f'The source "{source}" is not in ' \
                                          f'the list of assistants ' \
                                          f'{list(self.assistants.keys())}.'
        assistant = self.assistants[source]
        context = assistant.make_context(message=message)

        if assistant.uses_native_state(context=context):
            user_object = assistant.get_native_state(context=context)
        else:
            user_object = await self.get_user_object(context.user_id)
        context.add_user_object(user_object)
        return context

    async def get_user_object(self, user_id):
        if self.storage is None:
            return {}
        return self.storage.get(user_id)

    async def set_user_object(self, user_id, user_object):
        if self.storage is None:
            raise NotImplementedError()
        self.storage.set(user_id, user_object)

    async def standardize_output(self, source, original_message,
                                 response: Response):
        assert source in self.assistants, f'The source "{source}" is not in ' \
                                          f'the list of assistants ' \
                                          f'{list(self.assistants.keys())}.'
        return self.assistants[source].make_response(
            response=response,
            original_message=original_message
        )


@lru_cache()
def get_assistant_connector_service(
    dialog_manager: NLPDialogManager = Depends(get_nlp_dialog_manager),
) -> AssistantConnector:
    return AssistantConnector(
        dialog_manager=dialog_manager,
        alice_native_state=True,
    )
