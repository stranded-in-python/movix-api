SEARCH_FILMS_SUCCESS = [
    {
        "uuid": "996262ef-e565-426a-a25e-c6863eff474d",
        "title": "The Star",
        "imdb_rating": 6.2,
    },
    {
        "uuid": "68e9a139-976d-4a83-ad1b-e374376814c9",
        "title": "Star",
        "imdb_rating": 6.6,
    },
]

SEARCH_FILMS_NOT_FOUND = {"detail": "film not found"}

SEARCH_PERSONS_SUCCESS = [
    {
        "uuid": "6ba834a0-1039-4b5c-ab78-d5f1f18a4e7d",
        "full_name": "Carrie Beck",
        "films": [
            {
                "uuid": "a9d52337-3249-49ae-92b8-65ee9ebaf359",
                "title": "Star Wars Rebels",
                "imdb_rating": 8,
                "roles": ["writer"],
            },
            {
                "uuid": "5065b37b-fd5b-4c48-8a24-435198c44830",
                "title": "Star Wars Resistance",
                "imdb_rating": 4.9,
                "roles": ["writer"],
            },
            {
                "uuid": "754589c1-e304-4ed8-87bc-1ac897529b97",
                "title": "Lego Star Wars: The Freemaker Adventures",
                "imdb_rating": 7.5,
                "roles": ["writer"],
            },
            {
                "uuid": "75475f58-c0ea-4d6d-9f78-bb44d971a21f",
                "title": "Lego Star Wars: All-Stars",
                "imdb_rating": 6.5,
                "roles": ["writer"],
            },
        ],
    },
    {
        "uuid": "cbceaa01-910c-4f0e-b992-7faf7d27131a",
        "full_name": "Carrie Underwood",
        "films": [
            {
                "uuid": "01f81c66-d968-4375-bbb0-65103aa214d1",
                "title": "Carrie Underwood: An All-Star Holiday Special",
                "imdb_rating": 8.2,
                "roles": ["actor"],
            }
        ],
    },
]

SEARCH_PERSONS_NOT_FOUND = {"detail": "persons not found"}

UNPROCESSABLE = {
    "detail": [
        {
            "loc": ["path", "film_id"],
            "msg": "value is not a valid uuid",
            "type": "type_error.uuid",
        }
    ]
}
