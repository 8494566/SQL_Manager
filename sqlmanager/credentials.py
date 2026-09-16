"""Encrypted local credential store.

Replaces the legacy Windows-registry "remember password". Secrets are stored in
an encrypted file under the per-user app-data directory. No plaintext, no
registry. This is obfuscation-grade (the key sits next to the data) but is
strictly better than the legacy plaintext-registry value.
"""

from __future__ import annotations

import json
import os
import pathlib

from cryptography.fernet import Fernet, InvalidToken

_APP_DIR_NAME = "SQLManager"


def _app_dir() -> pathlib.Path:
    base = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
    root = pathlib.Path(base) if base else pathlib.Path.home()
    d = root / _APP_DIR_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


_STORE_FILE = _app_dir() / "credentials.bin"
_KEY_FILE = _app_dir() / "key.bin"


def _key() -> bytes:
    if _KEY_FILE.exists():
        return _KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    _KEY_FILE.write_bytes(key)
    return key


def save(data: dict) -> None:
    """Encrypt and persist the connection secrets dict."""
    token = Fernet(_key()).encrypt(json.dumps(data).encode("utf-8"))
    _STORE_FILE.write_bytes(token)


def load() -> dict | None:
    """Return the decrypted secrets dict, or None if absent/unreadable."""
    if not _STORE_FILE.exists():
        return None
    try:
        raw = Fernet(_key()).decrypt(_STORE_FILE.read_bytes())
        return json.loads(raw.decode("utf-8"))
    except (InvalidToken, ValueError, OSError):
        return None


def clear() -> None:
    """Delete the stored credentials (and key)."""
    for f in (_STORE_FILE, _KEY_FILE):
        try:
            f.unlink()
        except FileNotFoundError:
            pass
