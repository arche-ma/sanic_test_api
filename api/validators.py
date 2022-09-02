import re
from pydantic import BaseModel, validator, root_validator
from decimal import Decimal
from sanic.exceptions import SanicException
from typing import Optional
from utils import produce_signature
from sanic import Sanic


class UserScheme(BaseModel):
    username: str
    password: str

    @validator('password')
    def password_validation(cls, password):
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'

        if not re.match(pattern, password):
            raise SanicException(
                {'password': 'Password must be at least eight character '
                 'and contain at least one letter and one number'},
                status_code=400)
        return password


class AccountInputScheme(BaseModel):
    id: int


class ItemScheme(BaseModel):
    title: str
    description: str
    price: Decimal

    @validator('title')
    def title_validation(cls, title):
        if title == '':
            raise SanicException({'title': 'title may not be blank'},
                                 status_code=400)
        return title

    @validator('price')
    def price_validation(cls, price):
        if price <= 0:
            raise SanicException({'price': 'price should be bigger than 0'},
                                 status_code=400)
        return price


class ItemPatchScheme(ItemScheme):
    title: Optional[str]
    description: Optional[str]
    price: Optional[Decimal]


class WebhookScheme(BaseModel):
    signature: str
    transaction_id: int
    user_id: int
    bill_id: int
    amount: Decimal

    @classmethod
    def computed_signature(cls, transaction_id, user_id, bill_id, amount):
        app = Sanic.get_app('helloWorld')
        secret = app.config.SECRET
        signature = produce_signature(secret,
                                      transaction_id,
                                      user_id,
                                      bill_id,
                                      amount)
        return signature

    @root_validator
    def validate_signature(cls, values):
        validation_data = {key: value for (key, value) in values.items() if key != 'signature'}
        if values['signature'] != (sign := cls.computed_signature(**validation_data)):
            raise SanicException(f"signature is false: {sign}, {values}", 400)
        print(values)
        return values
