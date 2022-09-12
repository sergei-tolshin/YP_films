import time
import datetime as dt
import logging
from typing import Sequence
from pprint import pformat
import json
import sys

import psycopg2
from psycopg2.extras import NamedTupleCursor

from extractor.base import BasePGExtractor
from extractor.filmwork import FilmWorkExtractor
from extractor.genre import GenreExtractor
from extractor.person import PersonExtractor
from transformer.filmwork import transform_for_els as film_transformer
from transformer.genre import transform_for_els as genre_transformer
from transformer.person import transform_for_els as person_transformer
from loader.loader import bulk_upload_data
from loader.index import init_indices
from config import CONFIG

logging.basicConfig(
    level=logging.INFO, format='%(name)s: %(levelname)s at %(asctime)s: %(message)s'
)

logger = logging.getLogger('main')


def extract_data_for_index(
    dsn: dict, extractor: BasePGExtractor
) -> tuple[dt.datetime, Sequence]:
    with psycopg2.connect(**dsn, cursor_factory=NamedTupleCursor) as pg_conn:
        pg_extractor = extractor(pg_conn)
        current_timestamp, extracted_data = pg_extractor.extract()
        return current_timestamp, extracted_data


def etl_pipelines(for_test, number: int | None = None):
    dsn = CONFIG.pg.dsn.dict()
    extractors = (FilmWorkExtractor, GenreExtractor, PersonExtractor)
    transformers = (film_transformer, genre_transformer, person_transformer)

    for extractor_cls, transformer in zip(extractors, transformers):
        current_timestamp, data = extract_data_for_index(dsn, extractor_cls)
        els_query_data = transformer(data)
        if for_test:
            fname = f'{extractor_cls.name}_{number}.json'
            if els_query_data:
                with open(fname, 'w', encoding='utf-8') as file_:
                    json.dump(els_query_data, file_)
            errors = None
        else:
            _, errors = bulk_upload_data(els_query_data)
        if not errors:
            extractor_cls.state.set_state('timestamp', current_timestamp)
            logger.info(
                '%s: success upload chunk, current timestamp is %s',
                extractor_cls.name,
                current_timestamp
            )
        else:
            logger.error('%s', pformat(errors))


def main(test_):
    # generate json for test_data
    if test_:
        for i in range(5):
            etl_pipelines(test_, number=i)
        return

    # normal work
    init_indices()
    while True:
        etl_pipelines(False)
        time.sleep(CONFIG.extract_duration)


if __name__ == '__main__':
    test = len(sys.argv) == 2 and sys.arv[1] == 'test'
    main(test)
