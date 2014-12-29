#!/usr/bin/env python
# coding=utf-8

from multiprocessing import Process
import sys
import socket
import select
from encryption import TripleDESCipher
from config import HOST, PORT
import protocol

def client_process(sock):
    while 1:
        data = protocol.recv(sock)
        if not data:
            return sock.close()

        encryption = TripleDESCipher(data["key"])
        if data["encryption"] == 1:
            protocol.send(sock, encryption.encrypt(data["message"]))
        else:
            protocol.send(sock, encryption.decrypt(data["message"]))


def server(backlog=5, timeout=15):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(backlog)
    server_socket.setblocking(0)
    processes = []
    sockets = {server_socket}

    try:
        while 1:
            ready = select.select(sockets, [], [], timeout)
            for sock in ready[0]:
                if sock == server_socket:
                    conn, _ = server_socket.accept()
                    sockets.add(conn)
                    proc = Process(target=client_process, args=(conn,))
                    processes.append(proc)
                    proc.start()
                elif sock in sockets:
                    sock.close()
                    sockets.remove(sock)
    finally:
        # Ctrl-C
        for proc in processes:
            proc.terminate()
        server_socket.close()

if __name__ == "__main__":
    sys.exit(server())
