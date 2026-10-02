import hashlib
import hmac
import os


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError("Password is too long.")

    salt = os.urandom(16)

    hashed = hashlib.scrypt(
        password_bytes,
        salt=salt,
        n=16384,
        r=8,
        p=1
    )

    return (
        "scrypt$"
        + salt.hex()
        + "$"
        + hashed.hex()
    )


def verify_password(password: str, stored_password: str) -> bool:
    try:
        if not stored_password.startswith("scrypt$"):
            return False

        _, salt_hex, hash_hex = stored_password.split("$")

        salt = bytes.fromhex(salt_hex)
        password_bytes = password.encode("utf-8")

        if len(password_bytes) > 72:
            return False

        hashed = hashlib.scrypt(
            password_bytes,
            salt=salt,
            n=16384,
            r=8,
            p=1
        )

        return hmac.compare_digest(
            hashed.hex(),
            hash_hex
        )

    except Exception:
        return False

 