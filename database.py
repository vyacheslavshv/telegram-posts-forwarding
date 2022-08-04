import settings as stg

from tortoise import Tortoise
from tables import User


async def init():
    await Tortoise.init(stg.TORTOISE_ORM)
    await Tortoise.generate_schemas()

    tommy_db = await User.filter(id=5301984833).first()
    young_db = await User.filter(id=5448386746).first()

    if tommy_db:
        if not tommy_db.is_admin:
            tommy_db.is_admin = True
    else:
        tommy_db = User(id=5301984833, first_name='Tommy', is_admin=True)

    if young_db:
        if not young_db.is_admin:
            young_db.is_admin = True
    else:
        young_db = User(id=5448386746, first_name='Young', is_admin=True)

    await tommy_db.save()
    await young_db.save()
