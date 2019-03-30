#!/usr/bin/env python3
# from hashlib import sha256 as hash_alg
from hashlib import sha1 as hash_alg
import codecs
import secrets
import base64

block_size = hash_alg().block_size

opad = bytes((x ^ 0x5c) for x in range(2**8))
ipad = bytes((x ^ 0x36) for x in range(2**8))


# RFC 2104 compliant
def hmac(K, m):

    if len(K) > block_size:
        k = hash_alg(K).digest()
    else:
        k = K

    k = k.ljust(block_size, b'\0')

    o_key_pad = k.translate(opad) # xor(k, k.translate(opad))
    i_key_pad = k.translate(ipad) # xor(k, k.translate(ipad))

    inner = hash_alg(i_key_pad)
    outer = hash_alg(o_key_pad)

    inner.update(m)
    outer.update(inner.digest())

    return outer.digest()


def otp(secret, moving_factor):

    c = "%016x" % moving_factor
    c = codecs.decode(c, 'hex')

    r = hmac(secret, c)

    offset = r[-1] & 0xf
    code = (r[offset] & 0x7f) << 24
    code = code | ((r[offset + 1] & 0xff) << 16)
    code = code | ((r[offset + 2] & 0xff) << 8)
    code = code | ((r[offset + 3] & 0xff))

    res = code % 1e10

    return int(res)


def hotp(K, I):
    res = otp(K, I) % 1e6
    return int(res)


# TC = Time in seconds
def totp(K, TC, n=6):

    t = int(TC/30)
    res = otp(K, t) % (10**n)
    return int(res)


def int_2_str(i):

    a = (i >> 24) & 0xff
    b = (i >> 16)  & 0xff
    c = (i >> 8) & 0xff
    d = i & 0xff

    return "%c%c%c%c" % (a, b, c, d)


def gen_secret():
    # TODO Better randomness?
    return codecs.decode(base64.b32encode(secrets.token_bytes(32))).replace('=', '')


def bytes2hexs(b):
    return codecs.encode(b, "hex")


def str2hexs(s):
    res = codecs.encode(s)
    res = bytes2hexs(res)
    return res


# Método para utilizar secretos 2fa de webs
def web_secret_2_bytes(s):

    norm = s.replace(' ', '')
    norm += '=' * (len(norm) % 8)
    key = base64.b32decode(norm)

    return key
