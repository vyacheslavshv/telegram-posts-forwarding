import settings as stg

from tortoise import Tortoise
from tables import User


async def init():
    await Tortoise.init(stg.TORTOISE_ORM)
    await Tortoise.generate_schemas()

    vya_db = await User.filter(id=5091668827).first()
    ron_db = await User.filter(id=5448386746).first()

    if vya_db:
        if not vya_db.is_admin:
            vya_db.is_admin = True
    else:
        vya_db = User(id=5091668827, first_name='H', is_admin=True)

    if ron_db:
        if not ron_db.is_admin:
            ron_db.is_admin = True
    else:
        ron_db = User(id=5448386746, first_name='Young', is_admin=True)

    await vya_db.save()
    await ron_db.save()
