import re
from pydantic import BaseModel, validator, ValidationError
from decimal import Decimal
from sanic.exceptions import SanicException
from typing import Optional


class SanicPydanticScheme(BaseModel):
    @classmethod
    def validate(cls, *args, **kwargs):
        try:
            cls.validate(cls, *args, **kwargs)
        except ValidationError as e:
            raise SanicException(str(e.errors), status_code=400)


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


