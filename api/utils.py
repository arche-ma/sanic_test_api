import hashlib

from Crypto.Hash import SHA1


def get_hashed_password(password: str, secret="") -> str:
    salt_password = password + secret
    hashed_password = hashlib.md5(salt_password.encode())
    return hashed_password.hexdigest()


def produce_signature(private_key, transaction_id, user_id, bill_id, amount):
    signature = SHA1.new()
    signature.update(
        f"{private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}".encode()
    )
    return signature.hexdigest()
