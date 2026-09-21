"""
PRAHARI-NET Security and Cryptographic Utilities
Smart India Hackathon 2026 - Problem Statement SIH26178
"""
import hashlib
import hmac
import json
import base64
import time
from typing import Optional, Dict, Any
from backend.app.core.config import settings


def hash_password(password: str) -> str:
    """Secure password hashing using PBKDF2-HMAC-SHA256 with random salt."""
    import secrets
    salt = secrets.token_hex(16)
    iterations = 100_000
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    )
    return f"pbkdf2_sha256${iterations}${salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time verification of PBKDF2-HMAC-SHA256 passwords."""
    try:
        parts = hashed_password.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        iterations = int(parts[1])
        salt = parts[2]
        expected_hash = parts[3]
        
        computed = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        )
        return hmac.compare_digest(computed.hex(), expected_hash)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta_seconds: Optional[int] = None) -> str:
    """Generate HS256 JWT access token without external heavy dependencies."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    
    expires_in = expires_delta_seconds or (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    payload["exp"] = int(time.time()) + expires_in
    payload["iat"] = int(time.time())
    
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
    
    signature_base = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), signature_base, hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
    
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify HS256 JWT access token signature and expiration."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        encoded_header, encoded_payload, encoded_signature = parts
        
        # Verify signature
        signature_base = f"{encoded_header}.{encoded_payload}".encode()
        expected_signature = hmac.new(settings.SECRET_KEY.encode(), signature_base, hashlib.sha256).digest()
        
        # Base64 pad if needed
        padding = 4 - (len(encoded_signature) % 4)
        if padding != 4:
            encoded_signature_padded = encoded_signature + ('=' * padding)
        else:
            encoded_signature_padded = encoded_signature
            
        received_sig = base64.urlsafe_b64decode(encoded_signature_padded)
        if not hmac.compare_digest(expected_signature, received_sig):
            return None
            
        # Decode payload
        payload_padding = 4 - (len(encoded_payload) % 4)
        if payload_padding != 4:
            encoded_payload += '=' * payload_padding
        payload_bytes = base64.urlsafe_b64decode(encoded_payload)
        payload = json.loads(payload_bytes.decode())
        
        # Expiration check
        if payload.get("exp") and payload["exp"] < time.time():
            return None
            
        return payload
    except Exception:
        return None
