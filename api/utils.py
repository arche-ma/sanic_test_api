
from sanic import Sanic
from sanic.exceptions import SanicException
from sanic_jwt import exceptions
from sanic_jwt.decorators import inject_user
import hashlib

from models import User
from functools import wraps



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
    if not user:
        raise SanicException('User not found', 404)
    if not user.is_active:
        raise SanicException('activate your account first', 403)
    return dict(user_id=user.id, is_admin=user.is_admin)


async def retrieve_user(request, payload, *args, **kwargs):
    if payload:
        user_id = payload.get('user_id', None)
        user = await User.get(pk=user_id)
        return {'user_id': user.id,
                'is_admin': user.is_admin}
    else:
        return None


async def scopes(user, *args, **kwargs):
    if user['is_admin']:
        return ['user', 'admin']
    return ['user']


def is_active():
    def decorator(f):
        @wraps(f)
        @inject_user()
        async def decorated_function(request, user, *args, **kwargs):
            current_user = await User.get(pk=user['user_id'])
            if not current_user.is_active:
                raise exceptions.AuthenticationFailed('user is not activated')
            response = await f(request, user, *args, **kwargs)
            return response       
        return decorated_function
    return decorator
