#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Process, Manager, Lock, Condition, Queue
from contextlib import closing
import socket
import time

HOST = "127.0.0.1"
PORT = 5000

class ClientProcess(Process):
    def __init__(self, shared, condition, queue):
        Process.__init__(self)
        self._shared = shared
        self._condition = condition
        self._queue = queue
        self.start()

    def run(self):
        self._shared[self.pid] = 0
        while 1:
            self._condition.acquire()
            self._condition.wait(5)
            self._condition.release()
            if self._queue.qsize() > 1:
                # we have the task
                self._shared[self.pid] = 1 # execution
                with closing(socket.fromfd(self._queue.get(), S.AF_INET, S.SOCK_STREAM)) as sock:
                    self.handle(sock)
                self._shared[self.pid] = 0 # wait
            else:
                # wake up by timeout
                self._shared[self.pid] = 2 # terminated
                break


    def handle(self, sock):
        pass

class Server:
    def __init__(self, host, port, hots = 5):
        self._host = host
        self._port = port
        self._hots = hots
        manager = Manager()
        self._shared = manager.dict()
        self._condition = Condition()
        self._queue = Queue()
        self.processes = [ClientProcess(self._shared, self._condition, self._queue) for _ in xrange(hots)]

    def start(self):
        while(1):
            print self._shared
            time.sleep(1)

if __name__ == "__main__":
    s = Server(HOST, PORT)
    s.start()
