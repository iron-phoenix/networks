#!/usr/bin/env python
# coding=utf-8

from contextlib import closing
from gevent import socket
from config import HOST, PORT
import protocol
import random
import string
import time

def gen_str(length=16):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))

def send_request(sock, request):
    protocol.send(sock, request)
    return protocol.recv(sock)

def client_process(requests=100500, length=2**8):
    results = []
    with closing(socket.socket()) as sock:
        sock.connect((HOST, PORT))
        for _ in range(requests):
            key, message = gen_str(), gen_str(length)
            before = time.time()
            nclients, encrypted = send_request(sock, protocol.gen(key, message))
            results.append((nclients, (time.time() - before) * 1000.0))
            before = time.time()
            nclients, decrypted = send_request(sock, protocol.gen(key, encrypted, 0))
            results.append((nclients, (time.time() - before) * 1000.0))
            assert decrypted == message
    return results
