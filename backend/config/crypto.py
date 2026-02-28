import os
from cryptography.fernet import Fernet

FERNET_KEY = os.environ.get("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY is not set")

fernet = Fernet(FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY)

def encrypt_access_token(token: str) -> str:
    if not token:
        raise ValueError("token is required")
    return fernet.encrypt(token.encode("utf-8")).decode("utf-8")

def decrypt_access_token(token_enc: str) -> str:
    if not token_enc:
        raise ValueError("token_enc is required")
    return fernet.decrypt(token_enc.encode("utf-8")).decode("utf-8")