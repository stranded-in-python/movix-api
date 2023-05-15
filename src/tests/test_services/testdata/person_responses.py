PERSON_DETAILED_SUCCESS = {
    'films': [
        {
            'imdb_rating': 8.6,
            'roles': ['actor'],
            'title': 'Star Wars: Episode IV - A New Hope',
            'uuid': '3d825f60-9fff-4dfe-b294-1a45fa1e115d',
        },
        {
            'imdb_rating': 7.9,
            'roles': ['actor'],
            'title': 'Star Wars: Episode VII - The Force Awakens',
            'uuid': 'cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394',
        },
        {
            'imdb_rating': 7.6,
            'roles': ['actor'],
            'title': 'Star Wars: Episode V - The Empire Strikes Back: Deleted '
            'Scenes',
            'uuid': '4f53452f-a402-4a76-89fd-f034eeb8d657',
        },
        {
            'imdb_rating': 8.7,
            'roles': ['actor'],
            'title': 'Star Wars: Episode V - The Empire Strikes Back',
            'uuid': '0312ed51-8833-413f-bff5-0e139c11264a',
        },
        {
            'imdb_rating': 8.3,
            'roles': ['actor'],
            'title': 'Star Wars: Episode VI - Return of the Jedi',
            'uuid': '025c58cd-1b7e-43be-9ffb-8571a613579b',
        },
        {
            'imdb_rating': 2.1,
            'roles': ['actor'],
            'title': 'The Star Wars Holiday Special',
            'uuid': '134989c3-3b20-4ae7-8092-3e8ad2333d59',
        },
        {
            'imdb_rating': 7.7,
            'roles': ['actor'],
            'title': "From 'Star Wars' to 'Jedi': The Making of a Saga",
            'uuid': '3b1d0e70-42e5-4c9b-98cf-2681c420a99b',
        },
        {
            'imdb_rating': 4.8,
            'roles': ['actor'],
            'title': "Quentin Tarantino's Star Wars",
            'uuid': 'dbb9b244-483b-4592-9194-4938338419bc',
        },
        {
            'imdb_rating': 7.8,
            'roles': ['actor'],
            'title': 'Star Wars',
            'uuid': 'b6b8a3b7-1c12-45a8-9da7-4b20db8867df',
        },
        {
            'imdb_rating': 8.4,
            'roles': ['actor'],
            'title': 'Star Wars: Episode IV: A New Hope - Deleted Scenes',
            'uuid': 'f241a62c-2157-432a-bbeb-9c579c8bc18b',
        },
    ],
    'full_name': 'Harrison Ford',
    'uuid': '5b4bf1bc-3397-4e83-9b17-8b10c6544ed1',
}

PERSON_DETAILED_NOTFOUND = {"detail": "person not found"}

PERSON_DETAILED_UNPROCESSABLE = {
    "detail": [
        {
            "loc": ["path", "person_id"],
            "msg": "value is not a valid uuid",
            "type": "type_error.uuid",
        }
    ]
}
