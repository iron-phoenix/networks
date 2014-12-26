#!/usr/bin/env python

import sys
import socket
import select

from multiprocessig import Process, Pipe, reduction

HOST = '127.0.0.1'
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 5000

class ClientProcess(Process):
    # client process state
    WAIT       = 0
    EXECUTION  = 1

    def __init__(self, shared):
        Process.__init__(self)
        self._shared = shared
        self._sink, self._recv = Pipe()
        self.start()

    def run(self):
        self._shared[self.pid] = ClientProcess.WAIT
        while True:
            try:
                task = self._recv.recv()
                with self._lock:
                    conn = S.fromfd(reduction.recv_handle(self._recv), S.AF_INET, S.SOCK_STREAM)
                    try:
                        self._shared[self.pid] = ClientProcess.EXECUTION
                        self.handle(conn)
                        self._shared[self.pid] = ClientProcess.WAIT
                    finally:
                        conn.close()
            except:
                import traceback
                traceback.print_exc()


    def handle(self, sock):
        json = ""
        while 1:
            data = sock.recv(4096)
            json += data
            if data[-1] == "@":
                break
        json = json[:-1]
        sock.send(json + "@")

def chat_server(workers_count):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
 
    SOCKET_LIST.append(server_socket)

    workers = [ClientProcess() for i in xrange(workers_count)]
 
    while True:
        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST,[],[],0)
      
        for sock in ready_to_read:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                
		for w in workers:
                    if h.enqueue(Task.HANDLE):
                        reduction.send_handle(h._sink, conn.fileno(), h.pid)
             
            else:
                if sock in SOCKET_LIST:
                    SOCKET_LIST.remove(sock)
    server_socket.close()
 
if __name__ == "__main__":

    sys.exit(chat_server(16))
