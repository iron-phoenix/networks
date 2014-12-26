#!/usr/bin/env python
# coding=utf-8

import base64
from Crypto.Cipher import AES
from Crypto import Random

BS    = 16
PAD   = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
UNPAD = lambda s : s[:-ord(s[len(s)-1:])]

class AESCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, raw):
        raw = PAD(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return UNPAD(cipher.decrypt(enc[16:]))
