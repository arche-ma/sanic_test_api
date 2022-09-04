from sanic import Blueprint
from sanic.exceptions import SanicException
from sanic.response import HTTPResponse, json
from sanic_ext import validate
from sanic_jwt.decorators import scoped

from ..cruds.crud import (create_item, delete_item_by_id, get_item_by_id,
                          item_list, update_item)
from models import Account, Item
from ..utils import is_active
from ..validators import AccountInputScheme, ItemPatchScheme, ItemScheme

items = Blueprint('items', url_prefix='/items')


@items.post('/')
@scoped('admin')
@validate(json=ItemScheme)
async def post_item_handler(request, body: ItemScheme):
    item = await create_item(body)
    response = item.json(indent=4)
    return HTTPResponse(f'{{"item": {response}}}', status=201,
                        content_type='application/json')


@items.get('/')
@scoped('user')
@is_active(add_user=False)
async def get_items(request):
    items = await item_list()
    response = items.json(indent=4)
    return HTTPResponse(f'{{"items": {response}}}', status=200,
                        content_type='application/json')


@items.get('/<id:int>/')
@scoped('user')
@is_active(add_user=False)
async def item_by_id(request, id: int):
    item = await get_item_by_id(id)
    if item:
        response = item.json(indent=4)
        return HTTPResponse(f'{{"item:" {response}}}', status=200,
                            content_type='application/json')
    return json('item not found', status=404)


@items.delete('/<id:int>/')
@scoped('admin')
async def delete_item_handler(request, id: int):
    await delete_item_by_id(id)
    return json('ok', status=204)


@items.patch('/<id:int>/')
@scoped('admin')
@validate(json=ItemPatchScheme)
async def update_handler(request, body, id: int):
    updated_item = await update_item(id, item=body)
    response = updated_item.json(indent=4)
    return HTTPResponse(f'"{{item": {response}}}', status=200,
                        content_type='application/json')


@items.post('/<id:int>/buy/')
@scoped('user')
@is_active()
@validate(json=AccountInputScheme)
async def buy_item_handler(request, user, body: AccountInputScheme, id: int):
    account = await Account.get_or_none(pk=body.id, user__pk=user['user_id'])
    item = await Item.get_or_none(pk=id)
    if not item:
        raise SanicException('item doesn\'t exist')
    if not account:
        raise SanicException('account number is incorrect',
                             status_code=400)

    if item.price > account.balance:
        raise SanicException('insufficient funds', status_code=400)
    account.balance -= item.price
    await account.save(update_fields=['balance'])
    return json('success', status=200)
