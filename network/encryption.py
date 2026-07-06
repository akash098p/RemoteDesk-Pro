"""
===============================================================================
RemoteDesk Pro
File: network/encryption.py
Provides encryption and decryption functionality for secure communication.
Currently uses simple XOR cipher for demonstration purposes.
===============================================================================
"""

from typing import Union

class Encryption:
    """
    Simple encryption utility for RemoteDesk Pro.
    Uses XOR cipher with a secret key for basic encryption.
    """
    
    def __init__(self, key: Union[str, bytes] = "default_key"):
        """
        Initialize encryption utility.
        
        Args:
            key: Secret key for encryption/decryption (string or bytes)
        """
        if isinstance(key, str):
            self._key = key.encode('utf-8')
        else:
            self._key = key
    
    def encrypt(self, data: Union[bytes, str]) -> bytes:
        """
        Encrypt data using XOR cipher.
        
        Args:
            data: Data to encrypt (bytes or string)
            
        Returns:
            Encrypted bytes
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        key = self._key
        if len(key) < len(data):
            key = (key * ((len(data) // len(key)) + 1))[:len(data)]
            
        return bytes(b ^ k for b, k in zip(data, key))
    
    def decrypt(self, encrypted_data: Union[bytes, str]) -> Union[bytes, str]:
        """
        Decrypt encrypted data.
        
        Args:
            encrypted_data: Encrypted data (bytes or string)
            
        Returns:
            Decrypted data (bytes or string)
        """
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode('utf-8')
            
        key = self._key
        if len(key) < len(encrypted_data):
            key = (key * ((len(encrypted_data) // len(key)) + 1))[:len(encrypted_data)]
            
        return bytes(b ^ k for b, k in zip(encrypted_data, key))