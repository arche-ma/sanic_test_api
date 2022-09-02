
from enum import Enum
from uuid import uuid4
from tortoise import fields, Model


class Role(str, Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=100)
    password = fields.CharField(max_length=100)
    role = fields.CharEnumField(Role, default=Role.USER)
    is_active = fields.BooleanField(default=False)

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    class PydanticMeta:
        exclude = ['password']


class UserActivation(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User',
                                  related_name='activation_links',
                                  on_delete=fields.CASCADE)
    uuid_link = fields.UUIDField(default=uuid4)


class Item(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    price = fields.DecimalField(max_digits=10,
                                decimal_places=2)


class Account(Model):
    id = fields.IntField(pk=True)
    balance = fields.DecimalField(max_digits=10,
                                  decimal_places=2)
    user = fields.ForeignKeyField('models.User',
                                  related_name='accounts',
                                  on_delete=fields.CASCADE)

    class PydanticMeta:
        exclude = ['user']


class Transaction(Model):
    id = fields.IntField(pk=True)
    transaction_id = fields.IntField()
    datetime = fields.DatetimeField(auto_now=True)
    amount = fields.DecimalField(max_digits=10,
                                 decimal_places=2)
    account = fields.ForeignKeyField('models.Account',
                                     related_name='transactions')
