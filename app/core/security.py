import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from app.core.config import settings


def hash_secret(secret: str) -> str:
    salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, 200_000)
    return salt.hex() + ":" + hash_bytes.hex()


def verify_secret(secret: str, stored_hash: str) -> bool:
    try:
        salt_hex, expected_hex = stored_hash.split(":")
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    candidate_hash = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, 200_000).hex()
    return hmac.compare_digest(candidate_hash, expected_hex)


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(data: dict, expires_in: int = 3600) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_in

    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = hmac.new(settings.api_secret_key.encode(), f"{encoded_header}.{encoded_payload}".encode(), hashlib.sha256).digest()
    encoded_signature = _base64url_encode(signature)
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError:
        raise ValueError("Token JWT invalide")

    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    expected_signature = hmac.new(settings.api_secret_key.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(_base64url_encode(expected_signature), encoded_signature):
        raise ValueError("Signature JWT invalide")

    payload_bytes = _base64url_decode(encoded_payload)
    payload = json.loads(payload_bytes)
    if "exp" not in payload or int(payload["exp"]) < int(time.time()):
        raise ValueError("Token JWT expiré")
    return payload


def generate_api_key() -> str:
    return secrets.token_hex(24)
