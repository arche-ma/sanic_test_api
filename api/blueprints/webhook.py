from sanic import Blueprint, json
from sanic.exceptions import SanicException
from sanic_ext import validate
from validators import WebhookScheme
from models import User, Account, Transaction
from tortoise.transactions import atomic
webhook = Blueprint('webhook', url_prefix='/webhook')


@webhook.post('/')
@validate(WebhookScheme)
@atomic()
async def webhook_handler(request, body):
    """{
	“signature”: “f4eae5b2881d8b6a1455f62502d08b2258d80084”,
	“transaction_id”: 1234567,
	“user_id”: 123456,
	“bill_id”: 123456,
	“amount”: 100
}
"""
    user = await User.get_or_none(pk=body.user_id).prefetch_related('accounts')
    if not user:
        raise SanicException('User doesn\'t exist',
                             status_code=400)
    transaction = await Transaction.get_or_none(
        transaction_id=body.transaction_id)
    if transaction:
        raise SanicException('transaction already exists', status_code=400)
    account = await Account.get_or_none(pk=body.bill_id)
    if not account:
        account = await Account.create(user=user,
                                       balance=body.amount)
        await Transaction.create(amount=body.amount,
                                 account=account,
                                 transaction_id=body.transaction_id)
        return json('funds deposited')
    if account not in user.accounts:
        raise SanicException('user does\'t have given account',
                             status_code=400)
    account.balance += body.amount
    await account.save(update_fields=['balance'])
    await Transaction.create(amount=body.amount,
                                 account=account,
                                 transaction_id=body.transaction_id)
    return json('funds deposited')
