PERSON_DETAILED_SUCCESS = {
    'uuid': '5b4bf1bc-3397-4e83-9b17-8b10c6544ed1',
    'full_name': 'Harrison Ford',
    'films': [
        {
            'uuid': '0312ed51-8833-413f-bff5-0e139c11264a',
            'title': 'Star Wars: Episode V - The Empire Strikes Back',
            'imdb_rating': 8.7,
            'roles': ['actor'],
        },
        {
            'uuid': '134989c3-3b20-4ae7-8092-3e8ad2333d59',
            'title': 'The Star Wars Holiday Special',
            'imdb_rating': 2.1,
            'roles': ['actor'],
        },
        {
            'uuid': '3b1d0e70-42e5-4c9b-98cf-2681c420a99b',
            'title': "From 'Star Wars' to 'Jedi': The Making of a Saga",
            'imdb_rating': 7.7,
            'roles': ['actor'],
        },
        {
            'uuid': '3d825f60-9fff-4dfe-b294-1a45fa1e115d',
            'title': 'Star Wars: Episode IV - A New Hope',
            'imdb_rating': 8.6,
            'roles': ['actor'],
        },
        {
            'uuid': '4f53452f-a402-4a76-89fd-f034eeb8d657',
            'title': 'Star Wars: Episode V - The Empire Strikes Back: Deleted Scenes',
            'imdb_rating': 7.6,
            'roles': ['actor'],
        },
        {
            'uuid': 'b6b8a3b7-1c12-45a8-9da7-4b20db8867df',
            'title': 'Star Wars',
            'imdb_rating': 7.8,
            'roles': ['actor'],
        },
        {
            'uuid': 'c7bd11a4-30bf-4077-a618-97c3e5525427',
            'title': "The Characters of 'Star Wars'",
            'imdb_rating': 6.7,
            'roles': ['actor'],
        },
        {
            'uuid': 'cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394',
            'title': 'Star Wars: Episode VII - The Force Awakens',
            'imdb_rating': 7.9,
            'roles': ['actor'],
        },
        {
            'uuid': 'dbb9b244-483b-4592-9194-4938338419bc',
            'title': "Quentin Tarantino's Star Wars",
            'imdb_rating': 4.8,
            'roles': ['actor'],
        },
        {
            'uuid': 'f241a62c-2157-432a-bbeb-9c579c8bc18b',
            'title': 'Star Wars: Episode IV: A New Hope - Deleted Scenes',
            'imdb_rating': 8.4,
            'roles': ['actor'],
        },
    ],
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
