
from sanic import Sanic
from sanic.exceptions import SanicException
from sanic_jwt import exceptions
from sanic_jwt.decorators import inject_user
import hashlib
from Crypto.Hash import SHA1

from models import User
from functools import wraps


def get_hashed_password(password: str) -> str:
    app = Sanic.get_app('helloWorld')
    salt_password = password + app.config.SECRET
    hashed_password = hashlib.md5(salt_password.encode())
    return hashed_password.hexdigest()


def produce_signature(private_key, transaction_id, user_id, bill_id, amount):
    signature = SHA1.new()
    signature.update(
        f'{private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}'.encode()
    )
    return signature.hexdigest()


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
    return dict(user_id=user.id, is_admin=user.is_admin, is_active=user.is_active)


#set payload
async def retrieve_user(request, payload, *args, **kwargs):
    if payload:
        user_id = payload.get('user_id', None)
        user = await User.get(id=user_id)
        is_admin = user.is_admin
        is_active = user.is_active
        return {'user_id': user_id,
                'is_admin': is_admin,
                'is_active': is_active}
    else:
        return None


async def scopes(user, *args, **kwargs):
    if user['is_admin']:
        return ['user', 'admin']
    return ['user']


def is_active(add_user=True):
    def decorator(f):
        @wraps(f)
        @inject_user()
        async def decorated_function(request, user, *args, **kwargs):
            is_active = user.get('is_active', None)
            if not is_active:
                raise SanicException('user is not activated', 403)
            if add_user:
                response = await f(request, user, *args, **kwargs)
            else:
                response = await f(request, *args, **kwargs)
            return response
        return decorated_function
    return decorator

