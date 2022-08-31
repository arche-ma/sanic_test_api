import re
from pydantic import BaseModel, validator
from decimal import Decimal


class UserScheme(BaseModel):
    username: str
    password: str

    @validator('password')
    def password_validation(cls, password):
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'

        if not re.match(pattern, password):
            raise ValueError(
                'Password must be at least eight character'
                'and contain at least one letter and one number')
        return password


class ItemScheme(BaseModel):
    title: str
    description: str
    price: Decimal

    
class AccountInputScheme(BaseModel):
    id: int

