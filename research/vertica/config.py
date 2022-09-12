import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
PATH_TO_TEST_DATA_FIRST = "/test_data/first_part.csv"
PATH_TO_TEST_DATA_SECOND = "/test_data/second_part.txt"
PATH_TO_RESULTS = "/results/vertica.md"
SQL_QUERY_NUMBER = 100
CHUNK = 1000
TEST_VALUES = {
    "first": {"user_id": "id_3", "film_id": "film_id_44"},
    "second": {"user_id": "id_6", "film_id": "film_id_54"},
}
CONF_CONNECTION = {
    'host': os.getenv("CONNECTION_VERTICA_HOST", "127.0.0.1"),
    'port': os.getenv("CONNECTION_VERTICA_PORT", 5433),
    'user': os.getenv("CONNECTION_VERTICA_USER", "dbadmin"),
    'password': os.getenv("CONNECTION_VERTICA_PASS", ""),
    'database': os.getenv("CONNECTION_VERTICA_DB", "docker"),
    'autocommit': True,
    'use_prepared_statements': True
}
STRING_FOR_RESULTS = """
# Results vertica database testing.

* Average time single query to database without load new data - {time_without_load}.

* Average time first query process to database with load new data - {time_with_load_1}.

* Average time second query process to database with load new data - {time_with_load_2}.

* Average time query batching load new data ( with chunk value {chunk} ). - {time_load_batch}.
"""
