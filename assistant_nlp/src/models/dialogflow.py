from typing import Optional

import attr
from core.utils.serialization import FreeSerializeable, Serializeable


@attr.s
class Intent(Serializeable):
    name: str = attr.ib(default=None)
    displayName: str = attr.ib(default=None)


@attr.s
class Dialogflow(FreeSerializeable):
    queryText: str = attr.ib()
    action: str = attr.ib()
    parameters: dict = attr.ib(factory=dict)
    allRequiredParamsPresent: bool = attr.ib(default=False)
    fulfillmentText: str = attr.ib(default=None)
    fulfillmentMessages: list[str] = attr.ib(factory=list)
    outputContexts: list[str] = attr.ib(factory=list)
    intent: Optional[Intent] = attr.ib(default=None)
    intentDetectionConfidence: float = attr.ib(default=None)
    languageCode: str = attr.ib(default=None)

    @property
    def text(self):
        return self.fulfillmentText

    @property
    def all_required_params_present(self):
        return self.allRequiredParamsPresent

    def __get_payload(self, param):
        for dic in self.fulfillmentMessages:
            for key, value in dic.items():
                if key == 'payload':
                    return value.get(param, None)
        return None

    @property
    def suggests(self):
        return self.__get_payload('suggests')

    @property
    def response_variants(self):
        return self.__get_payload('response_variants')

    @property
    def no_data(self):
        return self.__get_payload('no_data')

    @property
    def not_found(self):
        return self.__get_payload('not_found')

    @property
    def prompts(self):
        return self.__get_payload('prompts')
