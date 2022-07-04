import settings as stg

from tortoise import Tortoise
from tables import User


async def init():
    await Tortoise.init(stg.TORTOISE_ORM)
    await Tortoise.generate_schemas()

    vya_db = await User.filter(id=134238838).first()
    ron_db = await User.filter(id=1836505766).first()

    if vya_db:
        if vya_db.is_admin:
            vya_db.is_admin = False
    else:
        vya_db = User(id=134238838, first_name='Vyacheslav', is_admin=False)

    if ron_db:
        if not ron_db.is_admin:
            ron_db.is_admin = True
    else:
        ron_db = User(id=1836505766, first_name='Niccolo', is_admin=True)

    await vya_db.save()
    await ron_db.save()
