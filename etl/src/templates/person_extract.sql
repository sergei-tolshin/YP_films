SELECT
    p.id as person_id,
    p.full_name,
    pfw.film_work_id,
    pfw.role as role_name
FROM content.person p
LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
WHERE p.id IN %(extraction_ids)s;
