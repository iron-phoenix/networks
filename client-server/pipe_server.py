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
        self.state = False
        self.start()

    def run(self):
        while 1:
            is_task = self.child.recv()
            self.state = True
            if is_task:
                client_socket = socket.fromfd(reduction.recv_handle(self.child), socket.AF_INET, socket.SOCK_STREAM)
                self.client_process(client_socket)
            self.state = False
                        
    def client_process(self, sock):
        while 1:
            data = protocol.recv(sock)
            if not data:
                return sock.close()

            encryption = TripleDESCipher(data["key"])
            if data["encryption"] == 1:
                protocol.send(sock, encryption.encrypt(data["message"]))
            else:
                protocol.send(sock, encryption.decrypt(data["message"]))

    def add_task(self):
        if not self.state:
            self.parent.send(True)
            return True
        return False

def server(backlog = 5):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(backlog)
    processes = []

    try:
        while 1:
            conn, addr = server_socket.accept()
            print "new client " + str(addr)
            task_send = False
            for p in processes:
                if p.add_task():
                    reduction.send_handle(p.parent, conn.fileno(), p.pid)
                    task_send = True
                    break
            if not task_send:
                p = ClientProcess()
                processes.append(p)
                p.add_task()
                reduction.send_handle(p.parent, conn.fileno(), p.pid)
    finally:
        # Ctrl-C
        for proc in processes:
            proc.terminate()
        server_socket.close()

if __name__ == "__main__":
    sys.exit(server())
