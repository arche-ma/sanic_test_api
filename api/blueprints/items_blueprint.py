from sanic.response import json
from sanic_ext import validate
from sanic import Blueprint
from sanic.exceptions import SanicException
from models import Account, User, Item

from cruds.crud import (item_list, create_item,
                        get_item_by_id, delete_item_by_id,
                        update_item)
from validators import ItemScheme, AccountInputScheme
from sanic_jwt.decorators import scoped, inject_user, protected

items = Blueprint('items', url_prefix='/items')


@items.post('/')
@scoped('admin')
@validate(json=ItemScheme)
async def post_item(request, body: ItemScheme):
    item = await create_item(body)
    return json(item.dict())


@items.get('/')
@scoped('user')
async def get_items(request):
    items = await item_list()
    return json(items.dict())


@items.get('/<id:int>/')
async def item_by_id(request, id: int):
    item = await get_item_by_id(id)
    if item:
        return json(item.dict())
    return json('item not found', status=404)


@items.delete('/<id:int>/')
async def delete_item(request, id: int):
    await delete_item_by_id(id)
    return json('ok', status=204)


@items.patch('/<id:int>/')
@validate(json=ItemScheme)
async def update_handler(request, body, id: int):
    updated_item = await update_item(id, item=body)
    return json(updated_item.dict(), status=200)


@items.post('/<id:int>/buy/')
@protected()
@inject_user()
@validate(json=AccountInputScheme)
async def buy_item(request, body: AccountInputScheme, user, id: int):
    user = await User.get(pk=user['user_id']).prefetch_related('accounts')
    item = await Item.get(pk=id)
    account = await Account.get_or_none(pk=body.id)
    if not account:
        raise SanicException('account number is incorrect',
                             status_code=400)
    if account not in user.accounts:
        raise SanicException('you don\'t have account with given number',
                             status_code=400)
    if item.price > account.balance:
        raise SanicException('insufficient funds')
    balance = account.balance - item.price
    await Account.get(id=body.id).update(balance=balance)
    return json('success',  status=200)
