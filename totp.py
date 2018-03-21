#!/usr/bin/env python3
from hashlib import sha1
import uuid

sha_block_size = 64

opad = b'k'* sha_block_size
ipad = b'm'* sha_block_size

def bytes2int(b):
    return int.from_bytes(b, byteorder='big', signed=False)

def encode(x):
    if type(x) == bytes:
        return x
    else:
        return x.encode()

def decode(x):
    if type(x) == bytes:
        return x.decode()
    else:
        return x

def xor(a, b):

    c = b''

    while len(a) > len(b):
        b = b'\x00' + b

    while len(b) < len(a):
        a = b'\x00' + a

    for i in range(len(a)):
        c += b'%c' % (a[i] ^ b[i])

    return c

def hmac(K, m):

    if len(K) > sha_block_size:
        k = sha1(K).digest()
    else:
        k = K

    while len(k) < sha_block_size:
        k = b'\x00' + k

    o_key_pad = xor(k, opad)
    i_key_pad = xor(k, ipad)

    a = sha1(encode(i_key_pad))
    a.update(encode(m))

    b = sha1(encode(o_key_pad))
    b.update(encode(a.digest()))

    return b.digest()


def hotp(K, C):
    return hmac(K.encode(), C.encode())

def totp(K, TC):
    return hotp(K, int_2_str(TC))


def int_2_str(i):

    a = (i >> 24) & 0xff
    b = (i >> 16)  & 0xff
    c = (i >> 8) & 0xff
    d = i & 0xff

    return "%c%c%c%c" % (a, b, c, d)

def gen_secret():
    return "%s%s" % (sha1(uuid.uuid4().bytes).hexdigest(), sha1(uuid.uuid4().bytes).hexdigest())
