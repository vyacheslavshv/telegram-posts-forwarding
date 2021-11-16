from tortoise import Tortoise


async def init():
    await Tortoise.init(
        db_url='sqlite://db_files/db.sqlite3',
        modules={'models': ['tables']})
    await Tortoise.generate_schemas()


class DataBase:

    def __init__(self):
        pass

