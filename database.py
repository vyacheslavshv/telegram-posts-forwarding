from tortoise import Tortoise
from tables import User


async def init():
    await Tortoise.init(
        db_url='sqlite://db_files/db.sqlite3',
        modules={'models': ['tables']})
    await Tortoise.generate_schemas()

    vya_db = await User.filter(id=134238838).first()
    ron_db = await User.filter(id=1836505766).first()

    if vya_db and not vya_db.is_admin:
        vya_db.is_admin = True
    else:
        vya_db = User(id=134238838, first_name='Vyacheslav', is_admin=True)

    if ron_db and not ron_db.is_admin:
        ron_db.is_admin = True
    else:
        ron_db = User(id=1836505766, first_name='Niccolo', is_admin=True)

    await vya_db.save()
    await ron_db.save()
