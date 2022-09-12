import json
from pymystem3 import Mystem

from aiohttp import ClientSession

from .settings import IAM_TOKEN, TRANSLATE_URL


async def translate(*args, target_language: str = 'en'):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Api-Key {0}'.format(IAM_TOKEN)}
    body = {
        'targetLanguageCode': target_language,
        'texts': args
    }
    async with ClientSession() as session:
        async with session.post(url=TRANSLATE_URL,
                                headers=headers,
                                data=json.dumps(body),
                                raise_for_status=True,
                                verify_ssl=False) as resp:
            data = await resp.json()

    return [_.get('text', '') for _ in data['translations']]


async def get_lemma(alice_request):
    m = Mystem()
    return list(
        filter(
            lambda x: x != ' ',
            m.lemmatize(alice_request.request.command)
        )
    )


async def get_obj_model_idx(lemmas, obj_model):
    if obj_model not in lemmas:
        return None
    obj_model_idx = lemmas.index(obj_model) + 1
    obj_title = None
    if obj_model_idx < len(lemmas):
        obj_title = lemmas[obj_model_idx]
        obj_title = await translate(obj_title)
    return obj_title
