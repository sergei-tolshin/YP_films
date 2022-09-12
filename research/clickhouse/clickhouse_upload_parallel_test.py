import asyncio
import time
from multiprocessing import Process

from clickhouse_driver import Client

import csv

client = Client(host='localhost')
start = time.time()


def execute_data(sql):
    start_sql = time.time()
    client.execute(sql)
    print(sql, '-', round(time.time() - start_sql, 4))


def execute_select_sql():
    for _ in range(5):
        queries = [
            'SELECT count() FROM default.test',
            'SELECT uniqExact(movie_id) FROM default.test',
            'SELECT uniqExact(user_id) FROM default.test',
            'SELECT user_id, uniqExact(movie_id) FROM default.test GROUP by user_id',
            "SELECT user_id, sum(viewed_frame), max(viewed_frame) FROM default.test WHERE user_id='id_5' GROUP by user_id",
            'SELECT user_id, sum(viewed_frame), max(viewed_frame) FROM default.test GROUP by user_id',
        ]
        for query in queries:
            execute_data(query)


def upload_data(start_value):
    with open('../test_data/first_part.csv', "r", newline='') as file:
        values = []
        file_data = csv.DictReader(file)
        for idx, line in enumerate(file_data, start=start_value):
            line['id'] = idx
            line['viewed_frame'] = int(line['viewed_frame'])
            values.append(line)
            if len(values) >= 100000:
                client.execute('INSERT INTO default.test (id, user_id, movie_id, viewed_frame) VALUES', values)
                values.clear()
        print('1kk records took', round(time.time() - start, 4))


def run_in_parallel():
    procs = [
        Process(
            target=upload_data,
            args=(1,)
        ),
        Process(
            target=upload_data,
            args=(10000000,)
        ),
        Process(target=execute_select_sql)
    ]

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()


run_in_parallel()
