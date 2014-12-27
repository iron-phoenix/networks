#!/usr/bin/env python
# coding=utf-8

import base64
from Crypto import Random
import pyDes

IV_LENGTH = 8

class TripleDESCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, raw):
        iv = Random.new().read(IV_LENGTH)
        cipher = pyDes.triple_des(self.key, pyDes.CBC, iv,
                                  pad=None, padmode=pyDes.PAD_PKCS5)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:IV_LENGTH]
        cipher = pyDes.triple_des(self.key, pyDes.CBC, iv,
                                  pad=None, padmode=pyDes.PAD_PKCS5)
        return cipher.decrypt(enc[IV_LENGTH:], padmode=pyDes.PAD_PKCS5)
