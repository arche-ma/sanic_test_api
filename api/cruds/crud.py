from sanic import exceptions
from tortoise.contrib.pydantic import (pydantic_model_creator,
                                       pydantic_queryset_creator)


from models import Item, User, UserActivation, Account
from utils import get_hashed_password
from validators import ItemScheme, UserScheme


item_output = pydantic_model_creator(Item)
item_list_output = pydantic_queryset_creator(Item)
user_output = pydantic_model_creator(User)
user_list_output = pydantic_queryset_creator(User)
account_output = pydantic_model_creator(Account)
account_user_output = pydantic_queryset_creator(Account)


async def create_item(ItemScheme: ItemScheme):
    new_item = await Item.create(
        title=ItemScheme.title,
        description=ItemScheme.description,
        price=ItemScheme.price
    )
    return await item_output.from_tortoise_orm(new_item)


async def get_item_by_id(id: int):
    item = await Item.get_or_none(pk=id)
    if item:
        return await item_output.from_tortoise_orm(item)
    return None


async def item_list():
    return await item_list_output.from_queryset(Item.all())


async def delete_item_by_id(id: int):
    await Item.get(pk=id).delete()


async def update_item(id, item: ItemScheme):
    update = item.dict()
    await Item.filter(pk=id).update(**update)
    item = await Item.get(pk=id)
    return await item_output.from_tortoise_orm(item)


async def create_user(user: UserScheme):
    if await User.get_or_none(username=user.username):
        raise ValueError('user with this username already exists')
    hashed_password = get_hashed_password(user.password)
    created_user = await User.create(
        username=user.username,
        password=hashed_password
    )
    user_activation = await UserActivation.create(user=created_user)
    return user_activation.uuid_link


async def get_user_by_uuid(uuid):
    user = await UserActivation.get(uuid_link=uuid)
    user = await user.user
    return user


async def get_user_by_id(id: int):
    user = await User.get_or_none(pk=id)
    if user:
        return await user_output.from_tortoise_orm(User)
    raise exceptions.SanicException('user not found',
                                    status_code=404)


async def users_list():
    users = User.all()
    return await user_list_output.from_queryset(users)


async def get_users_account(user_id: int):
    user = await User.get(pk=user_id).prefetch_related('accounts')
    accounts = user.accounts
    return await account_user_output.from_queryset(accounts.all())


async def deactivate_user(user_id):
    user = await User.get_or_none(pk=user_id)
    if user:
        user.is_active = False
        await user.save()
    else:
        exceptions.SanicException('User not found', status_code=404)


async def activate_user(user_id):
    user = await User.get_or_none(pk=user_id)
    if user:
        user.is_active = False
        await user.save()
    else:
        exceptions.SanicException('User not found', status_code=404)