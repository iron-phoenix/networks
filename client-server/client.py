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
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

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
    xses = [2 ** x for x in range(1, 10)] 
    results = [launch_client(client_counts) for client_counts in xses]
    plt.title('Client server')
    plt.xlabel("clients")
    plt.ylabel("ms")
    plt.xscale("log")
    plt.yscale("log")
    plt.plot(xses, results, "ro-")
    plt.show()
