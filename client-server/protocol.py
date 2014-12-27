#!/usr/bin/env python
# coding=utf-8

import msgpack
import struct

BUF_SIZE = 8196

def send(socket, msg):
    data = msgpack.packb(msg)
    return socket.send(struct.pack('>I', len(data)) + data)

def recv(socket):
    raw = socket.recv(BUF_SIZE)
    if not raw or len(raw) < 4:
        return None
    size = struct.unpack('>I', raw[:4])[0] - len(raw[4:])
    while size > 0:
        rest  = socket.recv(BUF_SIZE)
        raw  += rest
        size -= len(rest)
    assert size == 0
    return msgpack.unpackb(raw[4:])

def gen(key, message, encryption=1):
    return {"key": key, "message": message, "encryption": encryption}
