import time
from itertools import islice
from multiprocessing import Process, Array

import vertica_python

import config

RESULTS = {}


def create_table():
    """Create table for testing."""
    with vertica_python.connect(**config.CONF_CONNECTION) as connection:
        command = """
                CREATE TABLE views (
                    id IDENTITY,
                    user_id VARCHAR(256) NOT NULL,
                    movie_id VARCHAR(256) NOT NULL,
                    viewed_frame INTEGER NOT NULL
                );
                """
        cursor = connection.cursor()
        cursor.execute(command)


def copy_test_data(path_to_file: str):
    """Fill testing table with testing data."""
    with open(str(config.BASE_DIR) + path_to_file, "r") as file:
        with vertica_python.connect(**config.CONF_CONNECTION) as connection:
            cursor = connection.cursor()
            cursor.copy("COPY public.views (user_id, movie_id, viewed_frame) FROM stdin DELIMITER ',' ", file)


def load_batch_from_file(path_to_file: str) -> iter:
    """Batching read file with testing data."""
    with open(str(config.BASE_DIR) + path_to_file, "r") as file:
        for n_lines in iter(lambda: tuple(tuple(line.split(',')) for line in islice(file, config.CHUNK)), ()):
            yield n_lines


def test_aggregate_func(user_id: str, movie_id: str, arr: list) -> None:
    """Test single query to database."""
    time.sleep(5)
    with vertica_python.connect(**config.CONF_CONNECTION) as connection:
        for idx, _ in enumerate(arr):
            time_start = time.time()
            cursor = connection.cursor()
            command = """
                SELECT ROUND(SUM(viewed_frame)/COUNT(viewed_frame), 2) as viewed
                FROM views WHERE user_id='{user_id}' and movie_id ='{movie_id}';
                """.format(
                user_id=user_id,
                movie_id=movie_id
            )
            response = cursor.execute(command)
            result = response.fetchall()
            arr[idx] = time.time() - time_start


def test_exec_data_to_db(path_to_file: str, arr: list) -> None:
    """Batching load test data to database."""
    batch = load_batch_from_file(path_to_file)
    with vertica_python.connect(**config.CONF_CONNECTION) as connection:
        cursor = connection.cursor()
        for idx, part in enumerate(batch):
            time_start_exec = time.time()
            cursor.executemany(
                "INSERT INTO views (user_id, movie_id, viewed_frame) VALUES (?, ?, ?)",
                part,
                use_prepared_statements=True
            )
            executemany_time = time.time() - time_start_exec
            print("Executemany time - {}".format(executemany_time))
            arr[idx] = time.time() - time_start_exec


def drop_table():
    """Delete test table."""
    with vertica_python.connect(**config.CONF_CONNECTION) as connection:
        command = "drop table views;"
        cursor = connection.cursor()
        cursor.execute(command)


def write_result_to_file(path_to_file: str):
    with open(str(config.BASE_DIR) + path_to_file, "w") as file:
        file.write(
            config.STRING_FOR_RESULTS.format(
                time_without_load=RESULTS.get("TIME_WITHOUT_LOAD_TO_DB"),
                time_with_load_1=RESULTS.get("TIME_WITH_LOAD_TO_DB_1_PROCESS"),
                time_with_load_2=RESULTS.get("TIME_WITH_LOAD_TO_DB_2_PROCESS"),
                chunk=config.CHUNK,
                time_load_batch=RESULTS.get("TIME_LOAD_BATCH_TO_DB_")

            )
        )


def prepare_db():
    """Prepare database for testing."""
    create_table()
    copy_test_data(config.PATH_TO_TEST_DATA_FIRST)
    time.sleep(30)


def test_case_without_load():
    """Test query without load to DB."""
    results_without_load = [0] * 100
    test_aggregate_func(
        config.TEST_VALUES["first"]["user_id"],
        config.TEST_VALUES["first"]["film_id"],
        results_without_load
    )
    RESULTS["TIME_WITHOUT_LOAD_TO_DB"] = round(sum(results_without_load) / len(results_without_load), 4)
    time.sleep(10)


def test_case_with_load():
    """Test query with load to DB."""

    # Подгатавливаем три массива для мультипроцессинга
    result_query_1 = Array("f", config.SQL_QUERY_NUMBER)
    result_query_2 = Array("f", config.SQL_QUERY_NUMBER)
    result_load_to_db = Array("f", int(5000 / config.CHUNK))

    # Создаем три процесса
    procs = [
        Process(
            target=test_aggregate_func,
            args=(config.TEST_VALUES["first"]["user_id"], config.TEST_VALUES["first"]["film_id"], result_query_1)
        ),
        Process(
            target=test_aggregate_func,
            args=(config.TEST_VALUES["second"]["user_id"], config.TEST_VALUES["second"]["film_id"], result_query_2)
        ),
        Process(target=test_exec_data_to_db, args=(config.PATH_TO_TEST_DATA_SECOND, result_load_to_db))
    ]

    # Стартуем  три паралельных процесса. Один добаляет данные, два других в это время делают запрос к базе.
    for proc in procs:
        proc.start()

    # Ждем завершение трех дочерних процессов.
    for proc in procs:
        proc.join()

    # Вычисляем и сохраняем результат.
    RESULTS["TIME_WITH_LOAD_TO_DB_1_PROCESS"] = round(sum(result_query_1[:]) / config.SQL_QUERY_NUMBER, 4)
    RESULTS["TIME_WITH_LOAD_TO_DB_2_PROCESS"] = round(sum(result_query_2[:]) / config.SQL_QUERY_NUMBER, 4)
    RESULTS["TIME_LOAD_BATCH_TO_DB_"] = round(sum(result_load_to_db[:]) / (5000 / config.CHUNK), 4)


def runner():
    prepare_db()
    test_case_without_load()
    test_case_with_load()
    drop_table()


if __name__ == "__main__":
    runner()
    write_result_to_file(config.PATH_TO_RESULTS)
