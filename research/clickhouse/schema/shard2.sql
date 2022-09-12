CREATE DATABASE shard;

CREATE DATABASE replica;

CREATE TABLE shard.viewed_progress (
	`id` UInt64,
    `user_id` String,
    `movie_id` String,
    `viewed_frame` UInt64
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/viewed_progress', 'replica_1')
ORDER BY id;

CREATE TABLE replica.viewed_progress (
	`id` UInt64,
    `user_id` String,
    `movie_id` String,
    `viewed_frame` UInt64
) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/viewed_progress', 'replica_2')
ORDER BY id;

CREATE TABLE default.test (
	`id` UInt64,
    `user_id` String,
    `movie_id` String,
    `viewed_frame` UInt64
) ENGINE = Distributed('company_cluster', '', viewed_progress, rand());