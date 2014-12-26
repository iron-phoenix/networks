#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Process, Pool
from contextlib import closing
import socket
import sys
import string
import random
import json
import time
import matplotlib.pyplot as plt

HOST = "127.0.0.1"
PORT = 5000

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]

def gen_str():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

def send_request(sock, request):
    sock.send(request + "@")
    result = ""
    while 1:
        data = sock.recv(4096)
        result += data
        if data[-1] == "@":
            break
    return result[:-1]

def client_process():
    key, message = gen_str(), gen_str()
    start = time.time()
    with closing(socket.socket()) as sock:
        sock.connect((HOST, PORT))
        json_request = json.dumps({"key": key, "message": message, "encryption": 1})
        encrypted = send_request(sock, json_request)
        json_request = json.dumps({"key": key, "message": encrypted, "encryption": 0})
        decrypted = send_request(sock, json_request)
        assert decrypted == message
    elapsed = time.time() - start
    return elapsed

def launch_client(clients_count):
    p = Pool()
    asyncs = []
    for _ in xrange(clients_count):
        asyncs.append(p.apply_async(client_process))
    results = [r.get() for r in asyncs]
    return reduce(lambda a, b: a + b, results) / len(results)

if __name__ == "__main__":
    xses = [2 ** x for x in range(1, 2)]
    results = [launch_client(client_counts) for client_counts in xses]
    plt.title('Client server')
    plt.xlabel("clients")
    plt.ylabel("ms")
    plt.xscale("log")
    plt.yscale("log")
    plt.plot(xses, results, "ro-")
    plt.show()
