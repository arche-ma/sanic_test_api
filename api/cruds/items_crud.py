from sanic import exceptions
from tortoise.contrib.pydantic import (
    pydantic_model_creator,
    pydantic_queryset_creator,
)

from models import Item

from ..validators import ItemScheme

ItemOutput = pydantic_model_creator(Item)
ItemListOutput = pydantic_queryset_creator(Item)


async def create_item(ItemScheme: ItemScheme):
    new_item = await Item.create(
        title=ItemScheme.title,
        description=ItemScheme.description,
        price=ItemScheme.price,
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
        key: value
        for (key, value) in updated_data.items()
        if value is not None
    }
    if await Item.exists(pk=id):
        await Item.filter(pk=id).update(**updated_data)
        return await ItemOutput.from_tortoise_orm(await Item.get(pk=id))
    raise exceptions.SanicException("item doesn't exist", status_code=404)
