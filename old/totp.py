#!/usr/bin/env python3
import time
from hashlib import sha1
import uuid

sha_block_size = 64

opad = b'k'* sha_block_size
ipad = b'm'* sha_block_size

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

    return b.hexdigest()


def hotp(K, C):
    return hmac(K.encode(), C.encode())

def totp(K, TC):
    return hotp(K, int_2_str(TC))

# TODO Set start time
def get_time(slot_size):
    t = int(time.time())
    remainder = t % slot_size

    t -= remainder

    return t

def int_2_str(i):
    print(i)
    a = i >> 3*8
    b = (i >> 2*8) - (a << 8)
    c = (i >> 8) - (a << 2*8) - (b << 8)
    d = i - (a << 3*8) - (b << 2*8) - (c << 8)
    print(a)
    print(b)
    print(c)
    print(d)
    return "%c%c%c%c" % (a, b, c, d)

def gen_secret():
    return "%s%s" % (sha1(uuid.uuid4().bytes).hexdigest(), sha1(uuid.uuid4().bytes).hexdigest())

secret = gen_secret()
print("Secret: %s" % secret)

while 1:
    tc = get_time(30)
    print(totp(secret, tc))
    time.sleep(5)
