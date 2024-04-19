import hashlib

from cryptography.fernet import Fernet

import base64

def changeToByte(string:str):
    string_bytes = string.encode()
    sha256_hash = hashlib.sha256()
    sha256_hash.update(string_bytes)
    hashed_bytes = sha256_hash.digest()
    hashed_bytes = base64.urlsafe_b64encode(hashed_bytes)
    return hashed_bytes


def encyrptModule(text:str,key:str):
    key = changeToByte(key)
    cipher_suite = Fernet(key)
    plaintext = text.encode()
    ciphertext = cipher_suite.encrypt(plaintext)
    return ciphertext.decode()

def decryptModule(text:str, key:str):
    try:
        key = changeToByte(key)
        ciper_suite = Fernet(key)
        text = text.encode()
        plaintext = ciper_suite.decrypt(text)
        plaintext = plaintext.decode()
        return dict(status=True, msg=plaintext)
    except Exception:
        return dict(status=False, msg="Invalid key")


