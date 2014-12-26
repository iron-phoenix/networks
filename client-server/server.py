#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Process, Queue, Condition, reduction
import sys
import socket
import select
import json
from encryption import AESCipher

HOST = "127.0.0.1"
PORT = 5000
SOCKET_LIST = []

def handle(sock):
	jstr = ""

	while 1:
		data = sock.recv(4096)
		jstr += data
		if data[-1] == "@":
			break
	jstr = jstr[:-1]
        data = json.loads(jstr)
        encryption = AESCipher(data["key"])
        if data["encryption"] == 1:
                jstr = encryption.encrypt(data["message"])
        else:
                jstr = encryption.decrypt(data["message"])
	sock.send(jstr + "@")

def client_process(cond, queue):
	while True:
		cond.acquire()
		cond.wait()
		cond.release();
		client_handle = queue.get()
		file_descriptor = reduction.rebuild_handle(client_handle)
		sock = socket.fromfd(file_descriptor, socket.AF_INET, socket.SOCK_STREAM)
		handle(sock)
		sock.close()

def server(workers_count):
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((HOST, PORT))
	server_socket.listen(10)

	queue = Queue()

	cond = Condition()

	processes = [Process(target = client_process, args = (cond, queue, )) for _ in xrange(workers_count)]

	for p in processes:
		p.start()

	SOCKET_LIST.append(server_socket)

	try:
		while True:
			ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST,[],[],0)

			for sock in ready_to_read:
				if sock == server_socket:
					sockfd, addr = server_socket.accept()
					SOCKET_LIST.append(sockfd)

					client_handle = reduction.reduce_handle(sockfd.fileno())
					queue.put(client_handle)

					cond.acquire()
					cond.notify()
					cond.release();
				else:
					if sock in SOCKET_LIST:
						SOCKET_LIST.remove(sock)
	finally:
		for p in processes:
			p.terminate()
		server_socket.close()

if __name__ == "__main__":
    sys.exit(server(32))
