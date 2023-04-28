import orjson


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
