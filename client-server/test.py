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

    converges = False
    requests = 10
    while not converges:
        result = iteration(requests)
        for c in result:
            for x in c:
                if x[0] != clients_count:
                    print "Check me: actual:", x[0], "expected:", clients_count
        result = [[x[1] for x in c if x[0] == clients_count] for c in result]
        request_mean = [mean(x) for x in result]
        m  = mean(request_mean)
        outliers = [x for x in request_mean if abs(x - m) > 0.1 * m]
        if len(outliers) < 0.1 * requests:
            print "Hurray!", "outliers:", len(outliers)
            converges = True
        else:
            print "Failed requests:", requests, "outliers:", len(outliers)
        requests += 10

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
