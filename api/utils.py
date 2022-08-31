
from sanic import Sanic
from sanic_jwt import exceptions
import hashlib

from models import User


def get_hashed_password(password: str) -> str:
    app = Sanic.get_app('helloWorld')
    salt_password = password + app.config.SECRET
    hashed_password = hashlib.md5(salt_password.encode())
    return hashed_password.hexdigest()


async def authenticate(request):
    password = request.json.get('password')
    username = request.json.get('username')
    if not (password and username):
        raise exceptions.AuthenticationFailed(
            'authentication credentials were not provided'
        )
    password = get_hashed_password(password)
    user = await User.get_or_none(username=username,
                                  password=password)
    if user and user.is_active:
        return dict(user_id=user.id)
    
    raise exceptions.AuthenticationFailed(
        'authentication credentials are incorrect')


async def retrieve_user(request, payload, *args, **kwargs):
    if payload:
        user_id = payload.get('user_id', None)
        user = await User.get(pk=user_id)
        return {'user_id': user.pk,
                'is_admin': user.is_admin}
    else:
        return None


async def scopes(user, *args, **kwargs):
    if user['is_admin']:
        return ['user', 'admin']
    else:
        return ['user']

