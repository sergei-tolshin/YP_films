import logging

import backoff
from elasticsearch.helpers import bulk

from loader.service import get_es_service

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, Exception, max_tries=20, logger=logger)
def bulk_upload_data(data):
    el = get_es_service()
    res = bulk(el, data)
    return res
