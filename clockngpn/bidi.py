import pyqrcode
import os

OTPAUTH_URL = "otpauth://totp/{hostname}?secret={secret}&issuer={issuer}"


class OTPBidi():

    def __init__(self, secret):
        self._secret = secret.replace(' ', '')

    def generate(self):

        code = OTPAUTH_URL.format(
            **dict(
                hostname=os.uname().nodename,
                secret=self._secret,
                issuer='c-lock'
            )
        )

        qr = pyqrcode.create(code, error='L')
        return qr.terminal(quiet_zone=1)
