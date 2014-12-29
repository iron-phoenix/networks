#!/usr/bin/env python
# coding=utf-8

from multiprocessing import Process, Value
import sys
import socket
from encryption import TripleDESCipher
from config import HOST, PORT
import protocol

def client_process(sock, server_sock, timeout=15):
    server_sock.close()
    sock.settimeout(timeout)
    while 1:
        data = protocol.recv(sock)
        if not data:
            return sock.close()

        encryption = TripleDESCipher(data["key"])
        if data["encryption"] == 1:
            protocol.send(sock, encryption.encrypt(data["message"]))
        else:
            protocol.send(sock, encryption.decrypt(data["message"]))


def server(backlog=5):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(backlog)
    processes = []

    try:
        while 1:
            conn, addr = server_socket.accept()
            print "new client " + str(addr)
            proc = Process(target=client_process, args=(conn, server_socket))
            processes.append(proc)
            proc.start()
            conn.close()
    finally:
        # Ctrl-C
        for proc in processes:
            proc.terminate()
        server_socket.close()

if __name__ == "__main__":
    sys.exit(server())
