import json
import logging
from pathlib import Path

import backoff

from config import BASE_DIR
from loader.service import get_es_service
from state import MIN_TIMESTAMP, State, STATES

logger = logging.getLogger(__name__)

INDICES = ('movies', 'genre', 'person')


def get_index_fname(index_name: str) -> Path:
    return BASE_DIR / 'index' / f'{index_name}.json'


@backoff.on_exception(backoff.expo, Exception, max_tries=20, logger=logger)
def create_index(index_name: str, state: State):
    logger.info('create index: %s', index_name)
    el = get_es_service()
    index_fname = get_index_fname(index_name)

    with open(index_fname, encoding='utf-8') as mapping_file:
        body = json.load(mapping_file)

    if el.indices.exists([index_name]):
        logger.info('index %s exists, skip', index_name)
    else:
        logger.info('index %s not exists, create', index_name)
        el.indices.create(index=index_name, body=body)
        state.set_state('timestamp', MIN_TIMESTAMP)


def init_indices():
    for index_name, state in zip(INDICES, STATES):
        create_index(index_name, state)
