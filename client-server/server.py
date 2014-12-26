#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Process, Manager, Lock, Condition, Queue, reduction
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
        self._lock = Lock()
        self.start()

    def run(self, timeout=5):
        self._shared[self.pid] = ClientProcess.WAIT
        while 1:
            self._condition.acquire()
            self._condition.wait(timeout)
            self._condition.release()
            with self._lock:
                if not self._queue.empty():
                    print "New connection"
                    # we have the task
                    self._shared[self.pid] = ClientProcess.EXECUTION
                    client_handle = self._queue.get()
                    fd = reduction.rebuild_handle(client_handle)
                    with closing(socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)) as sock:
                        self.handle(sock)
                    self._shared[self.pid] = ClientProcess.WAIT
                else:
                    # wake up by timeout
                    self._shared[self.pid] = ClientProcess.TERMINATED
                    break


    def handle(self, sock):
        json = ""
        while 1:
            data = sock.recv(4096)
            json += data
            if data[-1] == "@":
                break
        json = json[:-1]
        sock.send(json + "@")

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
                print "New client"
                client_handle = reduction.reduce_handle(conn.fileno())
                self._queue.put(client_handle)

                if not self._queue.empty():
                    self.processes = [p for p in self.processes if self._shared[p.pid] != ClientProcess.TERMINATED]
                    self.processes.append(ClientProcess(self._shared, self._condition, self._queue))
                self._condition.acquire()
                self._condition.notify()
                self._condition.release()
        finally:
            for p in self.processes:
                p.join()
            soc.close()

if __name__ == "__main__":
    s = Server(HOST, PORT)
    s.start()
