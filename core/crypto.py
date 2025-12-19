import os
import string
import base64

"""
Crypto utilities for encrypting sensitive data.

NOTE ON DEPENDENCIES
--------------------
This module prefers the `cryptography` library's AESGCM implementation. On some
platforms (especially bleeding‑edge Python versions without prebuilt wheels),
`cryptography` may fail to import due to a missing `_cffi_backend` module.

Previously this caused the entire Django app to fail to start because the
import error was raised at module import time. To make the project runnable
in such environments, we now:

1. Try to import AESGCM from `cryptography`.
2. If that fails, fall back to a very simple XOR‑based cipher that is
   **NOT SECURE** and is intended only for local development and testing.

In production you MUST ensure that `cryptography` is installed correctly so
that the real AES‑GCM implementation is used.
"""

try:  # Prefer secure AESGCM from cryptography
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore[attr-defined]
    _CRYPTOGRAPHY_AVAILABLE = True
except Exception:  # pragma: no cover - environment specific failure
    AESGCM = None  # type: ignore[assignment]
    _CRYPTOGRAPHY_AVAILABLE = False


class _InsecureDevCipher:
    """
    Fallback cipher used ONLY when `cryptography` is unavailable.

    This implementation is intentionally simple and insecure – it just XORs the
    plaintext bytes with a repeating key and prefixes a random 12‑byte nonce so
    the interface matches AESGCM. This is sufficient for tests and local dev
    where strong encryption is not required.
    """

    def __init__(self, key: bytes):
        self.key = key

    def _xor(self, data: bytes, nonce: bytes) -> bytes:
        full_key = (self.key + nonce) * ((len(data) // (len(self.key) + len(nonce))) + 1)
        return bytes(b ^ k for b, k in zip(data, full_key[: len(data)]))

    def encrypt(self, nonce: bytes, data: bytes, associated_data=None) -> bytes:  # noqa: ARG002
        return self._xor(data, nonce)

    def decrypt(self, nonce: bytes, data: bytes, associated_data=None) -> bytes:  # noqa: ARG002
        return self._xor(data, nonce)

class CryptoManager:
    def __init__(self):
        # In production, this should come from HSM
        # Using a 32-byte key for AES-256
        env_key = os.getenv('MASTER_KEY')
        
        if env_key:
            # Try to decode if it looks like hex or base64, otherwise use as bytes
            try:
                # Naive check: if 64 hex chars, decode hex
                if len(env_key) == 64 and all(c in string.hexdigits for c in env_key):
                    self.master_key = bytes.fromhex(env_key)
                else:
                    self.master_key = env_key.encode('utf-8') if isinstance(env_key, str) else env_key
            except:
                self.master_key = env_key.encode('utf-8')
        else:
            # No key provided
            if os.getenv('DEBUG', 'False') == 'True':
                print("WARNING: MASTER_KEY not set. Using insecure fixed key for development.")
                self.master_key = b'0' * 32  # Fixed key for dev persistence
            else:
                from django.core.exceptions import ImproperlyConfigured
                raise ImproperlyConfigured("MASTER_KEY environment variable must be set in production.")

        # Ensure key is 32 bytes (pad or truncate if necessary for this simplistic impl, 
        # but in reality it should be exact)
        if len(self.master_key) < 32:
            self.master_key = self.master_key.ljust(32, b'0')
        elif len(self.master_key) > 32:
            self.master_key = self.master_key[:32]

        # Choose crypto backend
        if _CRYPTOGRAPHY_AVAILABLE and AESGCM is not None:
            self.aesgcm = AESGCM(self.master_key)
        else:
            # Development-only insecure fallback
            print(
                "WARNING: `cryptography` AESGCM backend is unavailable. "
                "Using insecure XOR-based cipher for development only. "
                "DO NOT use this configuration in production."
            )
            self.aesgcm = _InsecureDevCipher(self.master_key)

    def encrypt(self, plaintext: str) -> bytes:
        nonce = os.urandom(12)
        data = plaintext.encode('utf-8')
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def decrypt(self, ciphertext: bytes) -> str:
        nonce = ciphertext[:12]
        data = ciphertext[12:]
        plaintext = self.aesgcm.decrypt(nonce, data, None)
        return plaintext.decode('utf-8')

    def encrypt_to_b64(self, plaintext: str) -> str:
        encrypted = self.encrypt(plaintext)
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_from_b64(self, b64_text: str) -> str:
        encrypted = base64.b64decode(b64_text)
        return self.decrypt(encrypted)

crypto_manager = CryptoManager()
