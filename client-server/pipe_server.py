#!/usr/bin/env python
# coding=utf-8

from multiprocessing import Process, Value, Pipe, Lock, reduction
import sys
import socket
from encryption import TripleDESCipher
from config import HOST, PORT
import protocol

class ClientProcess(Process):
    def __init__(self):
        Process.__init__(self)
        self.parent, self.child = Pipe()
        self.state = Lock()
        self.start()

    def run(self):
        while 1:
            is_task = self.child.recv()
            self.state.acquire()
            if is_task:
                data = reduction.recv_handle(self.child)
                client_socket = socket.fromfd(data[0], socket.AF_INET, socket.SOCK_STREAM)
                active_clients = data[1]
                self.client_process(client_socket, active_clients)
            self.state.release()
                        
    def client_process(self, sock, active_clients):
        while 1:
            data = protocol.recv(sock)
            if not data:
                return sock.close()

            encryption = TripleDESCipher(data["key"])
            if data["encryption"] == 1:
                protocol.send(sock, (active_clients, encryption.encrypt(data["message"])))
            else:
                protocol.send(sock, (active_clients, encryption.decrypt(data["message"])))

    def add_task(self):
        if self.state.acquire(False):
            self.parent.send(True)
	    self.state.release()
            return True
        return False

def server(backlog = 5):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(backlog)
    processes = [ClientProcess() for x in xrange(10)]

    try:
        while 1:
            conn, addr = server_socket.accept()
            clients = 0
            for p in processes:
                if p.is_alive():
                    clients += 1
            print "new client " + str(addr)
            task_send = False
            for p in processes:
                if p.add_task():
                    reduction.send_handle(p.parent, (conn.fileno(), clients), p.pid)
                    client += 1
                    task_send = True
                    break
            if not task_send:
                p = ClientProcess()
                processes.append(p)
                p.add_task()
                reduction.send_handle(p.parent, (conn.fileno(), clients), p.pid)
                clients += 1
    finally:
        # Ctrl-C
        for proc in processes:
            proc.terminate()
            clients -= 1
        server_socket.close()

if __name__ == "__main__":
    sys.exit(server())
