#!/usr/bin/env python
# coding=utf-8

import gevent
import matplotlib.pyplot as plt
from client import client_process
from optparse import OptionParser
import math

def mean(xs, winzor_left=None):
    if winzor_left:
        xs.sort()
        xs = xs[int(winzor_left * len(xs)):]
    return sum(xs) / len(xs)

def stats(xs):
    avg = mean(xs)
    stddev = math.sqrt(mean([(x - avg) * (x - avg) for x in xs]))
    return avg, stddev

def launch_clients(clients_count):
    print clients_count
    def iteration(requests):
        jobs = [gevent.spawn(client_process, requests) for _ in range(clients_count)]
        gevent.joinall(jobs)
        return [r.value for r in jobs]

    requests = 15
    result = iteration(requests)
    request_mean = [mean([x[i] for x in result]) for i in range(5, requests - 5)]
    return stats(request_mean)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-m", "--max-clients", type="int",
                      help="Max number of clients",
                      dest="m", default=2**13)
    parser.add_option("-l", "--log-scale",
                      help="Both axes in log scale",
                      dest="l", action="store_true", default=False)
    parser.add_option("-o", "--output", type="string",
                      help="Output filename",
                      dest="o", default="out.png")
    (options, args) = parser.parse_args()

    xs = [2 ** x for x in range(int(math.log(options.m, 2)) + 1)]
    plt.title('TripleDES encryption/decryption server test')
    plt.xlabel("clients")
    plt.ylabel("response time in ms")

    if options.l:
        plt.xscale("log")
        plt.yscale("log")

    results = [launch_clients(client_counts) for client_counts in xs]
    avg, stddev = zip(*results)
    plt.errorbar(xs, avg, yerr=stddev)
    plt.plot(xs, avg)
    plt.savefig(options.o, bbox_inches='tight')
