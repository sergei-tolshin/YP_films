def transform_for_els(records):
    query_data = [
        {
            '_index': 'movies',
            '_id': record.fw_id,
            '_type': '_doc',
            'id': record.fw_id,
            'imdb_rating': record.rating,
            'min_access_level': record.min_access_level,
            'title': record.title,
            'description': record.description,
            'actors_names': [actor.name for actor in record.actors],
            'writers_names': [writer.name for writer in record.writers],
            'directors_names': [director.name for director in record.directors],
            'genres_names': [genre.name for genre in record.genres],
            'genres': [{'id': genre.id, 'name': genre.name} for genre in record.genres],
            'actors': [{'id': actor.id, 'name': actor.name} for actor in record.actors],
            'writers': [
                {'id': writer.id, 'name': writer.name} for writer in record.writers
            ],
            'directors': [
                {'id': director.id, 'name': director.name}
                for director in record.directors
            ],
        }
        for record in records
    ]
    return query_data
