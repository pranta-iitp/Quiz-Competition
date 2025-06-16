"""
Simple encryption utilities for user ID encryption
"""

import json
import base64
from cryptography.fernet import Fernet

# Instead of importing inside functions
from flask import current_app

def get_cipher_suite():
    """Get cipher suite using app's encryption key"""
    encryption_key = current_app.config.get('ENCRYPTION_KEY')
    if not encryption_key:
        raise ValueError("ENCRYPTION_KEY not found in app config")
    return Fernet(encryption_key)

def encrypt_user_id(user_id):
    """Encrypt user ID for URL"""
    try:
        cipher_suite = get_cipher_suite()
        encrypted_id = cipher_suite.encrypt(str(user_id).encode())
        # Make it URL-safe
        return base64.urlsafe_b64encode(encrypted_id).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def decrypt_user_id(encrypted_id):
    """Decrypt user ID from URL"""
    try:
        cipher_suite = get_cipher_suite()
        encrypted_data = base64.urlsafe_b64decode(encrypted_id.encode())
        decrypted_id = cipher_suite.decrypt(encrypted_data)
        return int(decrypted_id.decode())
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

# Optional: Functions for encrypting multiple values
def encrypt_multiple_values(**kwargs):
    """
    Encrypt multiple values as a dictionary
    Example: encrypt_multiple_values(user_id=123, role='admin')
    """
    if not kwargs:
        return None
        
    try:
        cipher_suite = get_cipher_suite()
        if not cipher_suite:
            raise ValueError("Could not get cipher suite")
            
        json_data = json.dumps(kwargs, separators=(',', ':'))  # Compact JSON
        encrypted_data = cipher_suite.encrypt(json_data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    except (json.JSONEncodeError, Exception) as e:
        print(f"Multi-value encryption error: {e}")
        return None

def decrypt_multiple_values(encrypted_token):
    """
    Decrypt multiple values back to dictionary
    """
    if not encrypted_token or not isinstance(encrypted_token, str):
        return None
        
    try:
        cipher_suite = get_cipher_suite()
        if not cipher_suite:
            raise ValueError("Could not get cipher suite")
            
        encrypted_data = base64.urlsafe_b64decode(encrypted_token.encode('utf-8'))
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode('utf-8'))
    except (base64.binascii.Error, json.JSONDecodeError, Exception) as e:
        print(f"Multi-value decryption error: {e}")
        return None