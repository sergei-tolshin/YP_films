SELECT id, updated_at
FROM {table_name}
WHERE updated_at > %(timestamp)s
ORDER BY updated_at
LIMIT %(limit)s;
