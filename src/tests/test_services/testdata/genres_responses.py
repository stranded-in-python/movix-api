GENRE_DETAILED_SUCCESS = {
    "uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
    "name": "Action",
    "popularity": 7.084836068700572,
    "description": None,
}

GENRE_DETAILED_NOTFOUND = {"detail": "genre not found"}

GENRE_DETAILED_UNPROCESSABLE = {
    "detail": [
        {
            "loc": ["path", "genre_id"],
            "msg": "value is not a valid uuid",
            "type": "type_error.uuid",
        }
    ]
}
