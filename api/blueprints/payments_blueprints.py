from sanic import Blueprint, json
from sanic.exceptions import SanicException
from sanic_ext import validate
from tortoise.transactions import atomic

from models import Account, Transaction, User

from ..validators import WebhookScheme

payments = Blueprint("payments", url_prefix="/payments")


@payments.post("/webhook")
@validate(WebhookScheme)
@atomic()
async def webhook_handler(request, body):
    user = await User.get_or_none(pk=body.user_id).prefetch_related("accounts")
    if not user:
        raise SanicException("User doesn't exist", status_code=400)
    transaction = await Transaction.get_or_none(
        transaction_id=body.transaction_id
    )
    if transaction:
        raise SanicException("transaction already exists", status_code=400)
    account = await Account.get_or_none(pk=body.bill_id)
    if not account:
        account = await Account.create(
            id=body.bill_id,
            user=user,
            balance=body.amount,
            on_conflict="DO NOTHING",
        )
        await Transaction.create(
            amount=body.amount,
            account=account,
            transaction_id=body.transaction_id,
        )
        return json("funds deposited")
    if account not in user.accounts:
        raise SanicException("user does't have given account", status_code=400)
    account.balance += body.amount
    await account.save(update_fields=["balance"])
    await Transaction.create(
        amount=body.amount, account=account, transaction_id=body.transaction_id
    )
    return json("funds deposited")
