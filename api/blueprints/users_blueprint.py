from sanic import Blueprint, Sanic
from sanic.response import HTTPResponse, json
from sanic_ext import validate
from sanic_jwt.decorators import scoped
from tortoise.transactions import atomic

from ..authentication_helpers import is_active
from ..cruds.users_crud import (
    create_user,
    delete_activation_link,
    get_user_by_id,
    get_user_by_uuid,
    get_user_transactions,
    get_users_account,
    set_user_state,
    users_list,
)
from ..validators import UserScheme

users = Blueprint("users", url_prefix="/users")


@atomic()
@users.post("/activate/<uuid:uuid>")
async def activation_link_handler(request, uuid):
    user_id = await get_user_by_uuid(uuid)
    await set_user_state(user_id, True)
    await delete_activation_link(uuid)
    return json("user was activated")


@users.post("/register/")
@validate(json=UserScheme)
async def register_handler(request, body: UserScheme):
    app = Sanic.get_app("helloWorld")
    uuid_link = await create_user(body)
    url = app.url_for("users.activation_link_handler", uuid=uuid_link)
    return json({"activate user with this url": f"{url}"})


@users.get("/me")
@is_active()
@scoped("user")
async def current_user_handler(request, user):
    user_id = user.get("user_id")
    response = await get_user_by_id(user_id)
    return HTTPResponse(
        response.json(indent=4), status=200, content_type="application/json"
    )


@users.get("/me/accounts")
@is_active()
@scoped(["user"])
async def my_accounts_handler(request, user):
    user_id = user.get("user_id")
    response = await get_users_account(user_id)
    return HTTPResponse(
        f'{{"accounts": {response.json(indent=4)}}}',
        status=200,
        content_type="application/json",
    )


@users.get("/me/transactions")
@is_active()
@scoped(["user"])
async def my_transactions_handler(request, user):
    user_id = user.get("user_id")
    response = await get_user_transactions(user_id)
    return json({"transactions": response}, status=200)


@users.get("/")
@is_active(add_user=False)
@scoped("admin")
async def all_users_handler(request):
    users = await users_list()
    response = users.json(indent=4)
    return HTTPResponse(
        f'{{"users": {response}}}', status=200, content_type="application/json"
    )


@users.get("/<id:int>")
@is_active(add_user=False)
@scoped("admin")
async def get_user_handler(request, id):
    user = await get_user_by_id(id)
    response = user.json(indent=4)
    return HTTPResponse(response, status=200, content_type="application/json")


@users.get("<user_id:int>/accounts")
@is_active(add_user=False)
@scoped("admin")
async def account_by_id_handler(request, user_id):
    accounts = await get_users_account(user_id=user_id)
    response = accounts.json(indent=4)
    return HTTPResponse(
        f'{{"accounts": {response}}}',
        status=200,
        content_type="application/json",
    )


@users.post("<user_id:int>/deactivate")
@is_active()
@scoped("admin")
async def deactivate_user_handler(request, user, user_id: int):
    await set_user_state(user_id, False)
    return json(f"user {user_id} was deactivated", status=200)


@users.post("<user_id:int>/activate")
@is_active(add_user=False)
@scoped("admin")
async def activate_user_handler(request, user_id: int):
    await set_user_state(user_id, True)
    return json(f"user {user_id} was activated", status=200)


@users.get("<user_id:int>/transactions")
@scoped("admin")
@is_active(add_user=False)
async def user_transactions_handler(request, user_id):
    response = {"transactions": await get_user_transactions(user_id=user_id)}
    return json(response, status=200)
