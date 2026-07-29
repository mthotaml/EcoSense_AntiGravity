"""
Security, Encryption, OAuth PKCE, and Privacy Sanitization Engine
"""

import base64
import hashlib
import os
import re
from cryptography.fernet import Fernet
from echosense.config import settings

# Initialize Fernet cipher with configuration key
try:
    _key_bytes = settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY
    _cipher = Fernet(_key_bytes)
except Exception:
    _key_bytes = Fernet.generate_key()
    _cipher = Fernet(_key_bytes)


def encrypt_token(plain_token: str) -> str:
    """Encrypt a sensitive OAuth token for storage at rest."""
    if not plain_token:
        return ""
    encrypted_bytes = _cipher.encrypt(plain_token.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted OAuth token."""
    if not encrypted_token:
        return ""
    try:
        decrypted_bytes = _cipher.decrypt(encrypted_token.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception:
        return ""


def generate_pkce_pair() -> tuple[str, str]:
    """Generate OAuth PKCE Code Verifier and S256 Code Challenge."""
    verifier_bytes = os.urandom(32)
    code_verifier = base64.urlsafe_b64encode(verifier_bytes).decode('utf-8').replace('=', '')
    
    sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').replace('=', '')
    
    return code_verifier, code_challenge


def sanitize_log_data(data: dict) -> dict:
    """
    Remove secrets, raw tokens, precise coordinates, and sensitive details from log dictionary.
    Guarantees compliance with Requirement GR-01 & FR-04.
    """
    sanitized = {}
    forbidden_keys = {'access_token', 'refresh_token', 'token', 'secret', 'password', 'latitude', 'longitude', 'raw_coords'}
    
    for k, v in data.items():
        if k.lower() in forbidden_keys:
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, str) and (("Bearer " in v) or len(v) > 80 and not v.startswith("http")):
            sanitized[k] = "[REDACTED_TOKEN]"
        else:
            sanitized[k] = v
            
    return sanitized
