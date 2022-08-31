from sanic import Sanic
from sanic_jwt import Initialize

from tortoise.contrib.sanic import register_tortoise
from tortoise import Tortoise
from blueprints.users_blueprint import users
from blueprints.items_blueprint import items
from utils import authenticate, retrieve_user, scopes

app = Sanic('helloWorld')

app.config.SECRET = 'my super secret key'
app.blueprint(users)
app.blueprint(items)

register_tortoise(
    app,
    db_url='postgres://postgres:secret_password@localhost:5432/postgres',
    modules={'models': ['models']},
    generate_schemas=True)

Initialize(app, authenticate=authenticate,
           retrieve_user=retrieve_user,
           scopes=scopes)

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)

