import re
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, condecimal, constr, root_validator, validator
from sanic import Sanic
from sanic.exceptions import SanicException

from .utils import produce_signature


class UserScheme(BaseModel):
    username: constr(min_length=3)
    password: constr(regex=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")


class AccountInputScheme(BaseModel):
    id: int


class ItemScheme(BaseModel):
    title: constr(min_length=3, max_length=20)
    description: constr(min_length=3, max_length=200)
    price: condecimal(gt=0)


class ItemPatchScheme(BaseModel):
    title: Optional[constr(min_length=3, max_length=20)]
    description: Optional[constr(min_length=3, max_length=200)]
    price: Optional[condecimal(gt=0)]


class WebhookScheme(BaseModel):
    signature: str
    transaction_id: int
    user_id: int
    bill_id: int
    amount: condecimal(gt=0)

    @classmethod
    def computed_signature(cls, transaction_id, user_id, bill_id, amount):
        app = Sanic.get_app("helloWorld")
        secret = app.config.SECRET
        signature = produce_signature(
            secret, transaction_id, user_id, bill_id, amount
        )
        return signature

    @root_validator
    def validate_signature(cls, values):
        validation_data = {
            key: value for (key, value) in values.items() if key != "signature"
        }
        if values["signature"] != (
            sign := cls.computed_signature(**validation_data)
        ):
            raise SanicException(f"signature is false: {sign}, {values}", 400)
        return values
