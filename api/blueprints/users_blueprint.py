from sanic import Sanic, Blueprint
from sanic.response import json
from sanic_ext import validate
from sanic_jwt.decorators import scoped
from cruds.crud import (get_user_by_uuid, create_user, get_user_by_id,
                        users_list, get_users_account, set_user_state)
from validators import UserScheme
from utils import is_active

users = Blueprint('users', url_prefix='/users')


@users.post('/activate/<uuid:uuid>')
async def activation_link_handler(request, uuid):
    user = await get_user_by_uuid(uuid)
    user.is_active = True
    await user.save()
    return json('user was activated')


@users.post('/register/')
@validate(json=UserScheme)
async def register_handler(request, body: UserScheme):
    app = Sanic.get_app('helloWorld')
    uuid_link = await create_user(body)
    url = app.url_for('users.activation_link_handler', uuid=uuid_link)
    return json({'activate user with this url': f'{url}'})


@users.get('/me')
@is_active()
@scoped('user')
async def current_user(request, user):
    user_id = user.get('user_id')
    response = await get_user_by_id(user_id)
    return json(response.dict(), status=200)


@users.get('/')
@scoped('admin')
async def all_users(request):
    response = await users_list()
    return json(response.dict(), status=200)


@users.get('/<id:int>')
@scoped('admin')
async def get_user_handled(request, id):
    user = await get_user_by_id(id)
    return json(user.dict(), status=200)


@users.get('/me/accounts')
@is_active()
@scoped(['user'])
async def my_accounts_handler(request, user):
    user_id = user.get('user_id')
    response = await get_users_account(user_id)
    return json(response.dict(), status=200)


@users.get('<user_id:int>/accounts')
@scoped('admin')
async def my_account_by_id_handler(request, user_id):
    accounts = await get_users_account(user_id=user_id)
    return json(accounts.dict(), status=200)


@users.post('<user_id:int>/deactivate')
@scoped('admin')
async def deactivate_user_handler(request, user_id: int):
    await set_user_state(user_id, False)
    return json(f'user {user_id} was deactivated', status=200)


@users.post('<user_id:int>/activate')
@scoped('admin')
async def activate_user_handler(request, user_id: int):
    await set_user_state(user_id, True)
    return json(f'user {user_id} was activated', status=200)
