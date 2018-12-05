#!/usr/bin/env python3
from hashlib import sha256 as hash_alg
import uuid

block_size = hash_alg().block_size

opad = bytes((x ^ 0x5c) for x in range(2**8))
ipad = bytes((x ^ 0x36) for x in range(2**8))

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

    a = a.ljust(len(b), '\0')
    b = b.ljust(len(a), '\0')

    for i in range(len(a)):
        c += b'%c' % (a[i] ^ b[i])

    return c

def hmac(K, m):
    # Rewritten according to RFC 2104
    if len(K) > block_size:
        k = hash_alg(K).digest()
    else:
        k = K

    # encode(k) because Key must always be bytes
    k = encode(k).ljust(block_size, b'\0')

    o_key_pad = k.translate(opad) # xor(k, k.translate(opad))
    i_key_pad = k.translate(ipad) # xor(k, k.translate(ipad))

    inner = hash_alg(encode(i_key_pad))
    outer = hash_alg(encode(o_key_pad))

    inner.update(encode(m))
    outer.update(encode(inner.digest()))

    return outer.digest()


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
    return "%s%s" % (hash_alg(uuid.uuid4().bytes).hexdigest(), hash_alg(uuid.uuid4().bytes).hexdigest())
