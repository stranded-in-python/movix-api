FILM_DETAILED_SUCCESS = {
    "uuid": "0312ed51-8833-413f-bff5-0e139c11264a",
    "title": "Star Wars: Episode V - The Empire Strikes Back",
    "imdb_rating": 8.7,
    "description": "Luke Skywalker, Han Solo, Princess Leia and Chewbacca face attack by the Imperial forces and its AT-AT walkers on the ice planet Hoth. While Han and Leia escape in the Millennium Falcon, Luke travels to Dagobah in search of Yoda. Only with the Jedi master's help will Luke survive when the dark side of the Force beckons him into the ultimate duel with Darth Vader.",
    "genres": [
        {"uuid": "120a21cf-9097-479e-904a-13dd7198c1dd", "name": "Adventure"},
        {"uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action"},
        {"uuid": "6c162475-c7ed-4461-9184-001ef3d9f26e", "name": "Sci-Fi"},
        {"uuid": "b92ef010-5e4c-4fd0-99d6-41b6456272cd", "name": "Fantasy"},
    ],
    "actors": [
        {"uuid": "26e83050-29ef-4163-a99d-b546cac208f8", "full_name": "Mark Hamill"},
        {"uuid": "5b4bf1bc-3397-4e83-9b17-8b10c6544ed1", "full_name": "Harrison Ford"},
        {"uuid": "b5d2b63a-ed1f-4e46-8320-cf52a32be358", "full_name": "Carrie Fisher"},
        {
            "uuid": "efdd1787-8871-4aa9-b1d7-f68e55b913ed",
            "full_name": "Billy Dee Williams",
        },
    ],
    "writers": [
        {
            "uuid": "3217bc91-bcfc-44eb-a609-82d228115c50",
            "full_name": "Lawrence Kasdan",
        },
        {"uuid": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a", "full_name": "George Lucas"},
        {"uuid": "ed149438-4d76-45c9-861b-d3ed48ccbf0c", "full_name": "Leigh Brackett"},
    ],
    "directors": [
        {"uuid": "1989ed1e-0c0b-4872-9dfb-f5ed13c764e2", "full_name": "Irvin Kershner"}
    ],
}

FILM_DETAILED_UNPROCESSABLE = {
    "detail": [
        {
            "loc": ["path", "film_id"],
            "msg": "value is not a valid uuid",
            "type": "type_error.uuid",
        }
    ]
}

FILM_DETAILED_NOTFOUND = {"detail": "film not found"}
