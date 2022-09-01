from sanic import exceptions
from tortoise.contrib.pydantic import (pydantic_model_creator,
                                       pydantic_queryset_creator)


from models import Item, User, UserActivation, Account
from utils import get_hashed_password
from validators import ItemScheme, UserScheme


ItemOutput = pydantic_model_creator(Item)
ItemListOutput = pydantic_queryset_creator(Item)
UserOutput = pydantic_model_creator(User)
UserListOutput = pydantic_queryset_creator(User)
AccountListOutput = pydantic_queryset_creator(Account)


async def create_item(ItemScheme: ItemScheme):
    new_item = await Item.create(
        title=ItemScheme.title,
        description=ItemScheme.description,
        price=ItemScheme.price
    )
    return await ItemOutput.from_tortoise_orm(new_item)


async def get_item_by_id(id: int):
    item = await Item.get_or_none(pk=id)
    if item:
        return await ItemOutput.from_tortoise_orm(item)
    return None


async def item_list():
    return await ItemListOutput.from_queryset(Item.all())


async def delete_item_by_id(id: int):
    await Item.get(pk=id).delete()


async def update_item(id, item: ItemScheme):
    updated_data = item.dict()
    updated_data = {
        key: value for (key, value) in updated_data.items()
        if value is not None
        }
    if await Item.exists(pk=id):
        await Item.filter(pk=id).update(**updated_data)
        return await ItemOutput.from_tortoise_orm(await Item.get(pk=id))
    raise exceptions.SanicException('item doesn\'t exist', status_code=404)


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
    user_link = await UserActivation.get_or_none(uuid_link=uuid)
    if not user_link:
        raise exceptions.SanicException('activation link not found',
                                        status_code=404)
    user = await user_link.user
    await user_link.delete()
    return user


async def get_user_by_id(id: int):
    user = await User.get_or_none(pk=id)
    if not user:
        raise exceptions.SanicException('user not found',
                                        status_code=404)
    return await UserOutput.from_tortoise_orm(user)


async def users_list():
    users = User.all()
    return await UserListOutput.from_queryset(users)


async def get_users_account(user_id: int):
    user = await User.get(pk=user_id).prefetch_related('accounts')
    accounts = user.accounts
    return await AccountListOutput.from_queryset(accounts.all())


async def set_user_state(user_id, is_active: bool):
    user = await User.get_or_none(pk=user_id)
    if user:
        user.is_active = is_active
        await user.save()
    else:
        exceptions.SanicException('User not found', status_code=404)

