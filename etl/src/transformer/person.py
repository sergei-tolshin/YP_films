def transform_roles(roles) -> list[dict[str, list]]:
    res = []
    for role_name, film_work_ids in roles.items():
        res.append({'role': role_name, 'film_work_ids': list(film_work_ids)})
    return res


def transform_for_els(records):
    query_data = [
        {
            '_index': 'person',
            '_id': record.person_id,
            '_type': '_doc',
            'id': record.person_id,
            'full_name': record.full_name,
            'roles': transform_roles(record.roles)
        }
        for record in records
    ]
    return query_data
