"""Encryption helpers for integration credentials at rest."""
from __future__ import annotations

import base64
import hashlib
import json
import os

from cryptography.fernet import Fernet, InvalidToken

from src.apps.api.config import get_settings


DEV_FALLBACK_KEY_SEED = "launchiq-dev-integration-key"


def _fernet_key_from_seed(seed: str) -> bytes:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _build_fernet() -> Fernet:
    settings = get_settings()
    seed = settings.integration_encryption_key.strip()
    is_test_env = settings.environment == "test" or bool(os.getenv("PYTEST_CURRENT_TEST"))
    if not seed:
        if not is_test_env:
            raise RuntimeError("integration_encryption_key must be set in non-test environments")
        seed = DEV_FALLBACK_KEY_SEED
    return Fernet(_fernet_key_from_seed(seed))


def encrypt_credentials(credentials: dict[str, object]) -> str:
    token = _build_fernet().encrypt(json.dumps(credentials).encode("utf-8"))
    return token.decode("utf-8")


def decrypt_credentials(encrypted_payload: str) -> dict[str, object]:
    try:
        raw = _build_fernet().decrypt(encrypted_payload.encode("utf-8"))
    except InvalidToken as exc:
        raise ValueError("Unable to decrypt integration credentials") from exc

    parsed = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("Decrypted integration credentials must be an object")
    return parsed
