from sanic import Sanic, Blueprint
from Crypto.Hash import SHA1


webhook = Blueprint('webhook', '/webhook')


def produce_signature(private_key, transaction_id, user_id, bill_id, amount):
    signature = SHA1.new()\
                    .update(
                        f'{private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}'.encode())\
                    .hexdigest()
    return signature


@webhook.post(/)
async def webhook_handler(request):
    """{
	“signature”: “f4eae5b2881d8b6a1455f62502d08b2258d80084”,
	“transaction_id”: 1234567,
	“user_id”: 123456,
	“bill_id”: 123456,
	“amount”: 100
}
"""
    