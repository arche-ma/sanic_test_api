from os import getenv

import aiofiles
from dotenv import load_dotenv
from tortoise import Tortoise, run_async

from api.utils import get_hashed_password
from models import Account, Item, User

load_dotenv()


async def init():

    await Tortoise.init(
        db_url='postgres://postgres:'
               f'{getenv("DB_PASSWORD")}@{getenv("DB_HOST")}:5432/postgres',
        modules={'models': ['models']},
    )
    await Tortoise.generate_schemas(safe=True)


async def generate_users(filename):
    async with aiofiles.open(filename, mode='r') as file:
        async for row in file:
            user_data = row.split(',')
            user_data[1] = get_hashed_password(user_data[1],
                                               getenv('SECRET'))
            user = {
                'username': user_data[0],
                'password': user_data[1],
                'role': user_data[2],
                'is_active': user_data[3]
            }
            user = await User.create(**user)
            print('user created')
            await generate_accounts(user)


async def generate_items(filename):
    async with aiofiles.open(filename, mode='r') as file:
        async for row in file:
            item_data = row.split(',')
            item = {
                'title': item_data[0],
                'description': item_data[1],
                'price': item_data[2]
                }
            await Item.create(**item)
            print('item created')


async def generate_accounts(user: User):
    account = {
        'id': 1000+user.pk,
        'balance': 1000000,
        'user': user
    }
    await Account.create(**account)
    print(f'account {account["id"]} created')


async def main():
    await init()
    if not await User.first():
        await generate_users('users.csv')
        await generate_items('items.csv')


if __name__ == '__main__':
    run_async(main())
