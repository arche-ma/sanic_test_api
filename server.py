import logging

from sanic import Sanic
from sanic_jwt import Initialize
from tortoise import run_async
from tortoise.contrib.sanic import register_tortoise

from api.authentication_helpers import authenticate, retrieve_user, scopes
from api.blueprints.items_blueprint import items
from api.blueprints.payments_blueprints import payments
from api.blueprints.users_blueprint import users
from config import config
from populate_w_textdata import main

logging.basicConfig(level=logging.DEBUG)
app = Sanic("helloWorld")


app.update_config(config)
app.blueprint(users)
app.blueprint(items)
app.blueprint(payments)

register_tortoise(
    app,
    db_url=config.db_url,
    modules={"models": ["models"]},
    generate_schemas=True,
)


Initialize(
    app,
    authenticate=authenticate,
    retrieve_user=retrieve_user,
    add_scopes_to_payload=scopes,
)


if __name__ == "__main__":
    run_async(main())
    app.run(host=app.config.HOST, port=app.config.PORT, dev=True)
