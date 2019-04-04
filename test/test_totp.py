import clockngpn.totp as totp
import codecs

K = 0x3132333435363738393031323334353637383930
S = codecs.decode("%x" % K, "hex")


# OTP TEST
def test_otp():
    assert totp.otp(S, 0) == 1284755224
    assert totp.otp(S, 1) == 1094287082
    assert totp.otp(S, 2) == 137359152
    assert totp.otp(S, 3) == 1726969429
    assert totp.otp(S, 4) == 1640338314
    assert totp.otp(S, 5) == 868254676
    assert totp.otp(S, 6) == 1918287922
    assert totp.otp(S, 7) == 82162583
    assert totp.otp(S, 8) == 673399871
    assert totp.otp(S, 9) == 645520489


# HOTP TEST
def test_hotp():
    assert totp.hotp(S, 0) == 755224
    assert totp.hotp(S, 1) == 287082
    assert totp.hotp(S, 2) == 359152
    assert totp.hotp(S, 3) == 969429
    assert totp.hotp(S, 4) == 338314
    assert totp.hotp(S, 5) == 254676
    assert totp.hotp(S, 6) == 287922
    assert totp.hotp(S, 7) == 162583
    assert totp.hotp(S, 8) == 399871
    assert totp.hotp(S, 9) == 520489


# TOTP TEST
def test_totp():
    assert totp.totp(S, 59, n=8) == 94287082
    assert totp.totp(S, 1111111109, n=8) == 7081804
    assert totp.totp(S, 1234567890, n=8) == 89005924
