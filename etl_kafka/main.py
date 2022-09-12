import json
from datetime import datetime

import backoff
from clickhouse_driver import Client
from kafka import KafkaConsumer, TopicPartition, OffsetAndMetadata
from kafka.consumer.fetcher import ConsumerRecord
from kafka.errors import NoBrokersAvailable

from config import Settings

settings = Settings()

MESSAGES_COUNT = settings.messages_count
MAX_TIMEOUT_BATCH = settings.max_timeout_batch


@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def insert_in_clickhouse(client, data: list) -> None:
    """
    Inserting data in clickhouse

    :param client: Clickhouse connection
    :param data: Data for load
    """
    client.execute(
        '''
        INSERT INTO default.viewed_progress (
        user_id,
        movie_id,
        viewed_frame,
        event_time
        )  VALUES {}
        '''.format(', '.join(i for i in data))
    )


def etl(consumer: KafkaConsumer, clickhouse_client: Client) -> None:
    """
    Transform data and load to Clickhouse

    :param consumer: Kafka consumer connection
    :param clickhouse_client: Clickhouse connection
    """

    start = int(datetime.now().timestamp())
    data = []
    while True:
        message_batch = consumer.poll(max_records=50000)

        for topic_partition, partition_batch in message_batch.items():
            if not data:
                data = partition_batch
            elif isinstance(partition_batch, list):
                for message in partition_batch:
                    data.append(message)
            elif isinstance(partition_batch, ConsumerRecord):
                data.append(partition_batch)

        time_diff = int(datetime.now().timestamp()) - start
        if len(data) >= MESSAGES_COUNT or time_diff >= MAX_TIMEOUT_BATCH:
            for message in data:
                prepared_data = [
                    (
                        str(
                            (
                                *str(message.key.decode('utf-8')).split('+'),
                                message.value,
                                datetime.fromtimestamp(message.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                            )
                        )
                    )
                ]
                insert_in_clickhouse(clickhouse_client, prepared_data)
                tp = TopicPartition(settings.kafka_topic, message.partition)
                options = {tp: OffsetAndMetadata(message.offset + 1, None)}
                consumer.commit(options)

                data.pop(0)
                start = int(datetime.now().timestamp())


@backoff.on_exception(backoff.expo, NoBrokersAvailable)
def main() -> None:
    """
    Main method

    """
    consumer = KafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=[f'{settings.kafka_host}:{settings.kafka_port}'],
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id='movies',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    clickhouse_client = Client(host=settings.clickhouse_host, port=settings.clickhouse_port)
    etl(consumer, clickhouse_client)


if __name__ == "__main__":
    main()
