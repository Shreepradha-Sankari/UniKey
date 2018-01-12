import os,binascii
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms)
from cryptography.hazmat.primitives.ciphers.modes import CBC

def pad(s):
    return s + ("\0" * (algorithms.AES.block_size - len(s) % algorithms.AES.block_size))

def encrypt(key,plain_text):
    msg=pad(plain_text)
    iv=os.urandom(16)
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), CBC(iv), backend=backend)
    encryptor=cipher.encryptor()
    ct = encryptor.update(msg.encode()) + encryptor.finalize()
    return ct,iv #ct,iv byte type

def decrypt(key,iv,cipher_text):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), CBC(iv), backend=backend)
    decryptor=cipher.decryptor()
    dt=decryptor.update(cipher_text)+decryptor.finalize()
    dt=dt.decode()
    return dt
