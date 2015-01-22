#!/usr/bin/env python
# coding=utf-8

import multiprocessing
from multiprocessing import Process, Value
import sys
import socket
from encryption import TripleDESCipher
from config import PORT
import protocol
import schedule

def client_process(sock, server_sock, nclients, timeout=60):
    server_sock.close()
    sock.settimeout(timeout)
    while 1:
        data = protocol.recv(sock)
        if not data:
            return sock.close()

        encryption = TripleDESCipher(data["key"])
        if data["encryption"] == 1:
            protocol.send(sock, (nclients.value, encryption.encrypt(data["message"])))
        else:
            protocol.send(sock, (nclients.value, encryption.decrypt(data["message"])))

def update_active_clients(nclients):
    print "update:", len(multiprocessing.active_children())
    nclients.value = len(multiprocessing.active_children())

def server(backlog=5):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', PORT))
    server_socket.listen(backlog)
    nclients = Value('i', 0)
    processes = []
    schedule.every(1).seconds.do(update_active_clients, nclients)

    try:
        while 1:
            conn, addr = server_socket.accept()
            print "new client " + str(addr)
            proc = Process(target=client_process, args=(conn, server_socket, nclients))
            processes.append(proc)
            proc.start()
            conn.close()
            nclients.value = len(multiprocessing.active_children())
    finally:
        # Ctrl-C
        for proc in processes:
            proc.terminate()
        server_socket.close()

if __name__ == "__main__":
    sys.exit(server())
