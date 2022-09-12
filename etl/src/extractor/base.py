import abc
import datetime as dt
import logging
from typing import Generator, NamedTuple

from psycopg2.extensions import connection as _connection

from config import IndexExtractSchema, QueryTemplates, BASE_DIR
from state import State, MIN_TIMESTAMP

logger = logging.getLogger(__name__)


class BasePGExtractor:
    def __init__(self, connection: _connection, schema: IndexExtractSchema, state: State):
        self._conn = connection
        self._schema = schema
        self._state = state

        tmpl_pathes: QueryTemplates = self._schema.query_templates
        self._tmpl_files = {}

        for name, path in tmpl_pathes.dict().items():
            file_path = BASE_DIR / path
            with open(file_path, encoding='utf-8') as tmpl_file:
                self._tmpl_files[name] = tmpl_file.read()

    def queryset(self, template, db_names, params) -> Generator[NamedTuple, None, None]:
        sql = template.format(**db_names)

        with self._conn.cursor() as cursor:
            cursor.execute(sql, params)
            for row in cursor.fetchall():
                yield row

    def get_extraction_ids(self) -> tuple[dt.datetime, tuple[str]]:

        extraction_ids = set()
        updated_tmpl = self._tmpl_files['updated']
        related_tmpl = self._tmpl_files['related']

        try:
            timestamp = self._state.get_state('timestamp')
        except FileNotFoundError:
            timestamp = MIN_TIMESTAMP

        current_timestamp = MIN_TIMESTAMP

        rel_updated_params = {'timestamp': timestamp, 'limit': self._schema.limit}

        related_tables = self._schema.related_tables or []
        for related_table in related_tables:
            db_names = related_table.dict()

            updated_ids = set()
            for record in self.queryset(updated_tmpl, db_names, rel_updated_params):
                updated_ids.add(record.id)

                if current_timestamp < record.updated_at:
                    current_timestamp = record.updated_at

            if updated_ids:
                params = {'limit': self._schema.limit, 'updated_ids': tuple(updated_ids)}
                db_names['table_name'] = self._schema.main_extraction_table

                for record in self.queryset(related_tmpl, db_names, params):
                    extraction_ids.add(record.id)

        db_names = {'table_name': self._schema.main_extraction_table}
        for record in self.queryset(updated_tmpl, db_names, rel_updated_params):
            extraction_ids.add(record.id)

            if current_timestamp < record.updated_at:
                current_timestamp = record.updated_at

        return max(current_timestamp, timestamp), tuple(extraction_ids)

    def extract(self) -> tuple[dt.datetime, Generator]:
        current_timestamp, extraction_ids = self.get_extraction_ids()
        if not extraction_ids:
            return current_timestamp, {}
        extraction_tmpl = self._tmpl_files['extract']
        params = {'extraction_ids': extraction_ids}
        queryset = self.queryset(extraction_tmpl, {}, params)
        extracted_data = self.group_extracted(queryset)
        return current_timestamp, extracted_data

    @staticmethod
    @abc.abstractmethod
    def group_extracted(queryset: Generator[NamedTuple, None, None]) -> Generator:
        pass
