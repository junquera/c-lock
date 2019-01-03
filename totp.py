#!/usr/bin/env python3
# from hashlib import sha256 as hash_alg
from hashlib import sha1 as hash_alg
import uuid
import codecs

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

# RFC 2104 compliant
def hmac(K, m):

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


def otp(secret, moving_factor):

    # Bytes of hexadecimal string
    s = str2hexs(secret)
    s = codecs.decode(s, 'hex')

    c = "%016x" % moving_factor
    c = codecs.decode(c, 'hex')

    r = hmac(s, c)

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
def totp(K, TC, n=8):

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
    return "%s%s" % (hash_alg(uuid.uuid4().bytes).hexdigest(), hash_alg(uuid.uuid4().bytes).hexdigest())


def bytes2hexs(b):
    return codecs.encode(b, "hex")

def str2hexs(s):
    res = codecs.encode(s)
    res = bytes2hexs(res)
    return res


if __name__ == '__main__':
    K = 0x3132333435363738393031323334353637383930
    S = codecs.decode(codecs.decode("%x" % K, "hex"))

    print("secret: ", S)

    # OTP TEST
    print("otp: ", otp(S, 0))

    # HOTP TEST
    print("hotp: ", hotp(S, 0))

    # TOTP TEST
    t = 59
    print("totp: ", totp(S, t))
