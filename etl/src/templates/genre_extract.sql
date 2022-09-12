SELECT
    g.id as g_id,
    g.name,
    g.created_at,
    g.updated_at as updated_at
FROM content.genre g
WHERE g.id IN %(extraction_ids)s
ORDER BY updated_at;
