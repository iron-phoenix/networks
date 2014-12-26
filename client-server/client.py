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

def gen_str():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randint(1, 1000)))

def client_process():
    request = {"key": gen_str(), "message": gen_str(), "encryption": random.randint(0, 1)}
    json_request = json.dumps(request)
    start = time.clock()
    with closing(socket.socket()) as sock:
        sock.connect((HOST, PORT))
        sock.send(json_request + "@")
        result = ""
        while 1:
            data = sock.recv(4096)
            result += data
            if data[-1] == "@":
                break
    return time.clock() - start

def launch_client(clients_count):
    p = Pool()
    asyncs = []
    for _ in xrange(clients_count):
        asyncs.append(p.apply_async(client_process))
    results = [r.get() for r in asyncs]
    return reduce(lambda a, b: a + b, results) / len(results)

if __name__ == "__main__":
    results = [launch_client(client_counts) for client_counts in range(1, 2000, 100)]
    plt.plot(range(1, 2000, 100), results, "ro-")
    plt.show()
