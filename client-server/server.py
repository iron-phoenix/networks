#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Process, Lock, Condition, Queue
from contextlib import closing
import socket
import time

HOST = "127.0.0.1"
PORT = 5000

class ClientProcess(Process):
    def __init__(self, condition, queue, lock):
        Process.__init__(self)
        self._condition = condition
        self._queue = queue
        self._lock = lock
        self.start()

    def run(self):
        while 1:
            self._condition.acquire()
            self._condition.wait()
            self._condition.release()
            self._lock.acquire()
            if self._queue.qsize() > 0:
                with closing(socket.fromfd(self._queue.get(), S.AF_INET, S.SOCK_STREAM)) as sock:
                    self.handle(sock)


    def handle(self, sock):
        pass

class Server:
    def __init__(self, host, port, hots = 5):
        self._host = host
        self._port = port
        self._hots = hots
        self._condition = Condition()
        self._queue = Queue()
        self._queue_lock = Lock()
        self.processes = [ClientProcess(self._condition, self._queue_lock) for _ in xrange(hots)]

    def start(self):
        while(1):
            time.sleep(1)

if __name__ == "__main__":
    s = Server(HOST, PORT)
    s.start()
