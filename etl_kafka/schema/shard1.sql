CREATE DATABASE shard;

CREATE DATABASE replica;

CREATE TABLE shard.viewed_progress
(
    `user_id`      String,
    `movie_id`     String,
    `viewed_frame` UInt64,
    `event_time`   DateTime
) Engine = ReplicatedMergeTree('/clickhouse/tables/shard2/viewed_progress', 'replica_1')
      PARTITION BY toYYYYMMDD(event_time)
      ORDER BY user_id;

CREATE TABLE replica.viewed_progress
(
    `user_id`      String,
    `movie_id`     String,
    `viewed_frame` UInt64,
    `event_time`   DateTime
) Engine = ReplicatedMergeTree('/clickhouse/tables/shard1/viewed_progress', 'replica_2')
      PARTITION BY toYYYYMMDD(event_time)
      ORDER BY user_id;

CREATE TABLE default.viewed_progress
(
    `user_id`      String,
    `movie_id`     String,
    `viewed_frame` UInt64,
    `event_time`   DateTime
) ENGINE = Distributed('yandex_practicum_cluster', '', viewed_progress, rand());
