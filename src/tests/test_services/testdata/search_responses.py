SEARCH_FILMS_SUCCESS = [
    {
        'uuid': '00e2e781-7af9-4f82-b4e9-14a488a3e184',
        'title': 'Star Wars: X-Wing',
        'imdb_rating': 8.1,
    },
    {
        'uuid': '01ab9e34-4ceb-4337-bb69-68a1b0de46b2',
        'title': 'Axl Rose: The Prettiest Star',
        'imdb_rating': 6.9,
    },
]

SEARCH_FILMS_NOT_FOUND = {"detail": "film not found"}

SEARCH_FILMS_UNPROCESSABLE_PAGE_NUMBER = {
    'detail': [
        {
            'loc': ['query', 'page_number'],
            'msg': 'ensure this value is greater than or equal to 1',
            'type': 'value_error.number.not_ge',
            'ctx': {'limit_value': 1},
        }
    ]
}
SEARCH_PERSONS_SUCCESS = [
    {
        'uuid': '6ba834a0-1039-4b5c-ab78-d5f1f18a4e7d',
        'full_name': 'Carrie Beck',
        'films': [
            {
                'uuid': '754589c1-e304-4ed8-87bc-1ac897529b97',
                'title': 'Lego Star Wars: The Freemaker Adventures',
                'imdb_rating': 7.5,
                'roles': ['writer'],
            },
            {
                'uuid': '75475f58-c0ea-4d6d-9f78-bb44d971a21f',
                'title': 'Lego Star Wars: All-Stars',
                'imdb_rating': 6.5,
                'roles': ['writer'],
            },
        ],
    },
    {
        'uuid': 'b5d2b63a-ed1f-4e46-8320-cf52a32be358',
        'full_name': 'Carrie Fisher',
        'films': [
            {
                'uuid': '0312ed51-8833-413f-bff5-0e139c11264a',
                'title': 'Star Wars: Episode V - The Empire Strikes Back',
                'imdb_rating': 8.7,
                'roles': ['actor'],
            },
            {
                'uuid': '12a8279d-d851-4eb9-9d64-d690455277cc',
                'title': 'Star Wars: Episode VIII - The Last Jedi',
                'imdb_rating': 7.0,
                'roles': ['actor'],
            },
        ],
    },
]

SEARCH_PERSONS_NOT_FOUND = {"detail": "persons not found"}

SEARCH_PERSONS_UNPROCESSABLE_PAGE_SIZE = {
    'detail': [
        {
            'loc': ['query', 'page_size'],
            'msg': 'ensure this value is greater than or equal to 1',
            'type': 'value_error.number.not_ge',
            'ctx': {'limit_value': 1},
        }
    ]
}
