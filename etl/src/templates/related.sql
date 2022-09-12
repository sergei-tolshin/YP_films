SELECT related_table.id, related_table.updated_at
FROM {table_name} related_table
LEFT JOIN {relations_table} relations_table ON relations_table.{related_id} = related_table.id
WHERE relations_table.{updated_id} IN %(updated_ids)s
ORDER BY related_table.updated_at
LIMIT %(limit)s;
