import imp
from sanic import Sanic
from sanic_jwt import Initialize
import logging
from tortoise.contrib.sanic import register_tortoise
from tortoise import Tortoise
from blueprints.users_blueprint import users
from blueprints.items_blueprint import items
from blueprints.webhook import webhook
from utils import authenticate, retrieve_user, scopes

logging.basicConfig(level=logging.DEBUG)
app = Sanic('helloWorld')

app.config.SECRET = 'my super secret key'
app.blueprint(users)
app.blueprint(items)
app.blueprint(webhook)

register_tortoise(
    app,
    db_url='postgres://postgres:secret_password@localhost:5432/postgres',
    modules={'models': ['models']},
    generate_schemas=True)

Initialize(app, authenticate=authenticate,
           retrieve_user=retrieve_user,
           add_scopes_to_payload=scopes)

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)

