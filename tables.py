from tortoise.models import Model
from tortoise import fields


class User(Model):

    id = fields.BigIntField(pk=True)
    first_name = fields.TextField(null=True)
    last_name = fields.TextField(null=True)
    username = fields.TextField(null=True)
    is_admin = fields.BooleanField(default=False)
    is_editor = fields.BooleanField(default=False)
    flow = fields.TextField(null=True)

    def __repr__(self):
        return f'User({self.id}, {self.first_name}, {self.last_name}, {self.username}, {self.is_admin}, ' \
               f'{self.is_editor}, {self.flow})'


class ClientUser(Model):

    id = fields.IntField(pk=True)
    phone_number = fields.TextField(null=True)
    phone_number_entered = fields.TextField(null=True)
    phone_code_hash = fields.TextField(null=True)

    def __repr__(self):
        return f'ClientUser({self.id}, {self.phone_number}, {self.phone_number_entered}, {self.phone_code_hash})'


class Category(Model):

    id = fields.IntField(pk=True)
    name = fields.TextField()

    transfers: fields.ReverseRelation["Transfer"]

    def __repr__(self):
        return f'Category({self.id}, {self.name})'


class Channel(Model):

    id = fields.BigIntField(pk=True)
    title = fields.TextField()
    username = fields.TextField(null=True)
    manual = fields.BooleanField(null=True, default=False)

    transfers: fields.ReverseRelation["Transfer"]

    def __repr__(self):
        return f'Channel({self.id}, {self.title}, {self.username}, {self.manual})'


class Transfer(Model):

    id = fields.IntField(pk=True)

    channel_from: fields.ForeignKeyRelation[Channel] = fields.ForeignKeyField(
        "models.Channel", related_name="transfers_from"
    )
    channel_to: fields.ForeignKeyRelation[Channel] = fields.ForeignKeyField(
        "models.Channel", related_name="transfers_to"
    )
    category: fields.ForeignKeyRelation[Category] = fields.ForeignKeyField(
        "models.Category", related_name="transfers"
    )

    is_working = fields.BooleanField()

    def __repr__(self):
        return f'Transfer({self.id}, {self.channel_from}, {self.channel_to}, {self.is_working}, {self.category})'


class StopWord(Model):

    id = fields.UUIDField(pk=True)
    word = fields.CharField(unique=True, max_length=100)

    def __repr__(self):
        return f'StopWord({self.id, self.word})'
