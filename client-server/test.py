#!/usr/bin/env python
# coding=utf-8

from multiprocessing import Pool
import matplotlib.pyplot as plt
from client import client_process
from optparse import OptionParser
import math

def launch_clients(clients_count, times):
    pool = Pool()
    asyncs = map(lambda _: pool.apply_async(client_process), range(clients_count))
    results = [r.get() for r in asyncs]
    return sum(results) / len(results)

if __name__ == "__main__":
    # TODO: impelement number of tests with variance and average
    #       maybe package statistics from python3?
    parser = OptionParser()
    parser.add_option("-m", "--max-clients", type="int",
                      help="Max number of clients",
                      dest="m", default=14)
    parser.add_option("-t", "--tests", type="int",
                      help="Number of tests",
                      dest="t", default=2)
    parser.add_option("-l", "--log-scale",
                      help="Both axes in log scale",
                      dest="l", action="store_true", default=False)
    parser.add_option("-o", "--output", type="string",
                      help="Output filename",
                      dest="o", default="out.png")
    (options, args) = parser.parse_args()

    xs = [2 ** x for x in range(int(math.log(options.m, 2)))]
    plt.title('Client-server')
    plt.xlabel("clients")
    plt.ylabel("ms")

    if options.l:
        plt.xscale("log")
        plt.yscale("log")

    results = [launch_clients(client_counts, options.t) for client_counts in xs]
    plt.plot(xs, results)
    plt.savefig(options.o, bbox_inches='tight')
