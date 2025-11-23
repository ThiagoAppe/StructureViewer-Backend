import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def load_key():
    """
    Load the encryption key from the LOG_ENCRYPTION_KEY environment variable.

    Returns:
        bytes: Decoded key used for AES-GCM operations.

    Raises:
        ValueError: If the environment variable is missing.
    """
    key = os.getenv("LOG_ENCRYPTION_KEY", None)
    if key is None:
        raise ValueError("LOG_ENCRYPTION_KEY not set")
    return base64.b64decode(key)


def encrypt_log(content: str) -> str:
    """
    Encrypt a log message using AES-GCM.

    Parameters:
        content (str): Text to encrypt.

    Returns:
        str: Base64-encoded encrypted payload including nonce.
    """
    key = load_key()
    aes = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aes.encrypt(nonce, content.encode("utf-8"), None)
    data = nonce + encrypted
    return base64.b64encode(data).decode("utf-8")


def decrypt_log(encoded: str) -> str:
    """
    Decrypt an encrypted log message encoded in Base64.

    Parameters:
        encoded (str): Base64 encrypted text including nonce.

    Returns:
        str: Decrypted text.
    """
    key = load_key()
    aes = AESGCM(key)
    data = base64.b64decode(encoded)
    nonce = data[:12]
    encrypted = data[12:]
    decrypted = aes.decrypt(nonce, encrypted, None)
    return decrypted.decode("utf-8")
