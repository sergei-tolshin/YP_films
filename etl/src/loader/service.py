import logging
from functools import lru_cache

import backoff
import elasticsearch as els

from config import CONFIG

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, Exception, max_tries=20, logger=logger)
@lru_cache()
def get_es_service():
    logger.debug('initialize es service...')
    host = CONFIG.elastic.host
    port = CONFIG.elastic.port
    el = els.Elasticsearch(f'{host}:{port}')
    return el
