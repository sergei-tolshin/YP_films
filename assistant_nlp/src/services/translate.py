import json
from functools import lru_cache

from aiohttp import ClientSession
from core.config import settings


class Translate:
    def __init__(self) -> None:
        self.url = settings.TRANSLATE_URL
        self.client = ClientSession
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Api-Key {0}'.format(settings.TRANSLATE_TOKEN)
        }

    async def translate(self, *texts, target_language: str = 'en',
                        one_item=False):
        body = {
            'targetLanguageCode': target_language,
            'texts': texts
        }
        async with self.client() as session:
            async with session.post(url=self.url,
                                    headers=self.headers,
                                    data=json.dumps(body),
                                    raise_for_status=True,
                                    verify_ssl=False) as response:
                data = await response.json()

        results = [_.get('text', '') for _ in data['translations']]

        if one_item:
            return results[0]
        return results


@lru_cache()
def get_translate_service() -> Translate:
    return Translate()
