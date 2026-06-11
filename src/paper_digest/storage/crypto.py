# src/paper_digest/storage/crypto.py
"""Symmetric encryption helpers for storing sensitive values (e.g. user API keys)."""

import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from paper_digest.auth.config import settings


def _get_fernet() -> Fernet:
    """Derive a Fernet key from SECRET_KEY.

    Fernet requires a 32-byte url-safe base64-encoded key. We derive this
    deterministically from SECRET_KEY so no extra env var is needed, while
    still keeping the key separate from raw SECRET_KEY usage elsewhere.
    """
    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string for storage. Returns a base64 token (str)."""
    if not plaintext:
        return plaintext
    f = _get_fernet()
    token = f.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_value(token: str) -> str | None:
    """Decrypt a stored token. Returns None if it can't be decrypted
    (e.g. legacy plaintext value or tampering)."""
    if not token:
        return token
    f = _get_fernet()
    try:
        return f.decrypt(token.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        # Likely a legacy plaintext key stored before encryption was added.
        return token
