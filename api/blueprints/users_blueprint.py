from sanic import Sanic
from sanic.response import json
from sanic_ext import validate
from sanic import Blueprint
from sanic_jwt.decorators import scoped, inject_user
from cruds.crud import get_user_by_uuid, create_user, get_user_by_id, users_list, get_users_account, activate_user, deactivate_user
from validators import UserScheme

users = Blueprint('users', url_prefix='/users')


@users.post('/activate/<uuid:uuid>')
async def activate_user(request, uuid):
    user = await get_user_by_uuid(uuid)
    user.is_active = True
    user.save()
    return json('user was activated')


@users.post('/register/')
@validate(json=UserScheme)
async def register_handler(request, body: UserScheme):
    app = Sanic.get_app('helloWorld')
    uuid_link = await create_user(body)
    url = app.url_for('users.activate_user', uuid=uuid_link)
    return json({'activate user with this url': f'{url}'})



@users.get('/me')
@inject_user()
async def current_user(request, user):
    print(user)
    user_id = user.get('user_id')
    response = await get_user_by_id(user_id)
    return json(response.dict(), status=200)


@users.get('/')
@scoped('user')
async def all_users(request, user):
    response = await users_list()
    return json(response.dict(), status=200)


@users.get('/me/accounts')
@scoped(['user'])
@inject_user()
async def my_accounts_handler(request, user):
    print(user)
    user_id = user.get('user_id')
    response = await get_users_account(user_id)
    return json(response.dict(), status=200)


@users.get('<user_id:int>/accounts')
async def my_account_by_id_handler(request, user_id):
    accounts = await get_users_account(user_id=user_id)
    return json(accounts.dict(), status=200)


@users.post('<user_id:int>/deactivate')
@scoped('admin')
async def deactivate_user_handler(request, user_id: int):
    await deactivate_user(user_id)


@users.post('<user_id:int>/activate')
@scoped('admin')
async def activate_user_handler(request, user_id: int):
    await activate_user(user_id)
