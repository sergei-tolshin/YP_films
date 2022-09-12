import os
import dataclasses as dc
import sqlite3
from pathlib import Path

import logging

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_values

from models import ALL_DATA

logger = logging.getLogger("migrator")

CHUNK_SIZE = 1000


class SQLiteLoader:
    def __init__(self, connection):
        self._conn = connection

    def load_table(self, table_name, model_class):
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * from {table_name}")
        while rows := cursor.fetchmany(CHUNK_SIZE):
            chunk = []
            for row in rows:
                chunk.append(model_class(*row))
            yield chunk

    def load_all_data(self):
        for table_name, model_class in ALL_DATA:
            for chunk in self.load_table(table_name, model_class):
                yield chunk, table_name


class PostgresSaver:
    def __init__(self, connection):
        self._conn = connection

    def save_table(self, table_name, records):
        columns = tuple(dc.asdict(records[0]).keys())
        fields = ", ".join(columns)

        with self._conn.cursor() as cur:
            statement = f"insert into content.{table_name} ({fields}) values %s"
            execute_values(cur, statement, map(dc.astuple, records))

    def save_all_data(self, data):
        for rows_chunk, table_name in data:
            self.save_table(table_name, rows_chunk)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    data = sqlite_loader.load_all_data()
    postgres_saver.save_all_data(data)


def make_dsn():
    dsn = {
        'host': os.environ.get("POSTGRES_HOST", "localhost"),
        'port': os.environ.get("POSTGRES_PORT", 5432),
        'dbname': os.environ.get("POSTGRES_DB", 'movies_database'),
        'user': os.environ.get("POSTGRES_USER", 'mvadmin'),
        'password': os.environ.get("POSTGRES_PASSWORD", None),
    }
    return dsn


def main():
    dsn = make_dsn()
    logger.info("start data migration")
    try:
        sqlite_path = Path(__file__).parent / 'db.sqlite'
        with sqlite3.connect(sqlite_path) as sqlite_conn, psycopg2.connect(**dsn, cursor_factory=DictCursor) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
    finally:
        logger.debug("closing sqlite connection")
        sqlite_conn.close()
    logger.info("data migration done")


if __name__ == '__main__':
    main()
