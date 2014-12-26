#!/usr/bin/env python
# coding=utf-8

from multiprocessing import Pool
import matplotlib.pyplot as plt
from client import client_process

def launch_clients(clients_count):
    pool = Pool()
    asyncs = map(lambda _: pool.apply_async(client_process), range(clients_count))
    results = [r.get() for r in asyncs]
    return sum(results) / len(results)

if __name__ == "__main__":
    xs = [2 ** x for x in range(9)]
    results = [launch_clients(client_counts) for client_counts in xs]
    plt.title('Client server')
    plt.xlabel("clients")
    plt.ylabel("ms")
    plt.xscale("log")
    plt.yscale("log")
    plt.plot(xs, results, "ro-")
    plt.show()
