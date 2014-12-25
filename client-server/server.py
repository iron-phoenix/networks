#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Process, Manager, Lock, Condition, Queue
from contextlib import closing
import socket
import time

HOST = "127.0.0.1"
PORT = 5000

class ClientProcess(Process):
    # client process state
    WAIT       = 0
    EXECUTION  = 1
    TERMINATED = 2

    def __init__(self, shared, condition, queue):
        Process.__init__(self)
        self._shared = shared
        self._condition = condition
        self._queue = queue
        self.start()

    def run(self, timeout=5):
        self._shared[self.pid] = ClientProcess.WAIT
        while 1:
            self._condition.acquire()
            self._condition.wait(timeout)
            self._condition.release()
            if not self._queue.empty():
                # we have the task
                self._shared[self.pid] = ClientProcess.EXECUTION
                with closing(socket.fromfd(self._queue.get(), socket.AF_INET, socket.SOCK_STREAM)) as sock:
                    self.handle(sock)
                self._shared[self.pid] = ClientProcess.WAIT
            else:
                # wake up by timeout
                self._shared[self.pid] = ClientProcess.TERMINATED
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

    def start(self, max_queued_connections=5):
        try:
            soc = socket.socket()
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            soc.bind((self._host, self._port))
            soc.listen(max_queued_connections)

            while 1:
                (conn, addr) = soc.accept()
                free_id = -1
                for p in self.processes:
                    if self._shared[p.pid] == ClientProcess.WAIT:
                        free_id = p.pid
                        break
                if free_id == -1:
                    p = ClientProcess(self._shared, self._condition, self._queue)
                    self.processes.append(p)
                self._queue.enqueue(conn.fileno())
        finally:
            for p in self.processes:
                p.close()
                p.join()
            soc.close()

if __name__ == "__main__":
    s = Server(HOST, PORT)
    s.start()
