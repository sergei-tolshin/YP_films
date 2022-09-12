def transform_for_els(records):
    query_data = [
        {
            '_index': 'genre',
            '_id': f'{record.g_id}',
            '_type': '_doc',
            'id': record.g_id,
            'name': record.name,
        }
        for record in records
    ]
    return query_data
