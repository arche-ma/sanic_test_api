import logging
from os import getenv

from dotenv import load_dotenv
from sanic import Sanic
from sanic_jwt import Initialize
from tortoise import run_async
from tortoise.contrib.sanic import register_tortoise

from api.blueprints.items_blueprint import items
from api.blueprints.users_blueprint import users
from api.blueprints.webhook import webhook
from api.utils import authenticate, retrieve_user, scopes

from populate_w_textdata import main

logging.basicConfig(level=logging.DEBUG)
app = Sanic('helloWorld')
load_dotenv()


app.config.SECRET = getenv('SECRET')
app.blueprint(users)
app.blueprint(items)
app.blueprint(webhook)

register_tortoise(
    app,
    db_url=f'postgres://postgres:{getenv("DB_PASSWORD")}@{getenv("DB_HOST")}:5432/postgres',
    modules={'models': ['models']},
    generate_schemas=True)


Initialize(app, authenticate=authenticate,
           retrieve_user=retrieve_user,
           add_scopes_to_payload=scopes)


if __name__ == '__main__':
    run_async(main())
    app.run(host='0.0.0.0', port=8000, dev=True)
