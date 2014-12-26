#!/usr/bin/env python

import sys
import socket
import select

from multiprocessing import Process, Pipe, Manager, reduction

HOST = '127.0.0.1'
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 5000

def handle(sock):
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

    while True:
        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST,[],[],0)
      
        for sock in ready_to_read:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                
		handle(sockfd)
             
            else:
                if sock in SOCKET_LIST:
                    SOCKET_LIST.remove(sock)
    server_socket.close()
 
if __name__ == "__main__":

    sys.exit(chat_server(16))
