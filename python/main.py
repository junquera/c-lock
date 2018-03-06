import totp
import time

def bytes2int(b):
    return int.from_bytes(b, byteorder='big', signed=False)

# 1 < n < 10
def gen_ports(val, n=3, forbidden=[]):
    values = []
    for i in range(n):
        aux = bytes2int(val[2*i:(2*i)+2])
        if aux < 1024:
            aux += 1024
        while aux in forbidden or aux in values:
            aux+=1
        values.append(aux)
    return values

# TODO Threading & sockets!
# import threading, socket

class TocTocPorts():

    def __init__(self, secret, n_ports=4, slot=30, forbidden=[]):

        self._secret = secret
        self._slot = slot
        self._forbidden = forbidden

        if n_ports > 20:
            raise "Error, max ports: %d" % 20

        self._n_ports = n_ports

        ports = self.get_all()

        self._p = ports['p']
        self._a = ports['a']
        self._n = ports['n']

        # time.sleep(ns)

    def next(self):
        t = int(time.time())
        remainder = t % self._slot

        return self._slot - remainder


    def last(self):
        t = int(time.time())
        remainder = t % self._slot

        return t - remainder

    def get_all(self):

        tc = self.last()
        tcp = tc - self._slot
        tcn = tc + self._slot

        valp = totp.totp(self._secret, tcp)
        vala = totp.totp(self._secret, tc)
        valn = totp.totp(self._secret, tcn)

        portsp = gen_ports(valp, n=self._n_ports, forbidden=self._forbidden)
        portsa = gen_ports(vala, n=self._n_ports, forbidden=self._forbidden)
        portsn = gen_ports(valn, n=self._n_ports, forbidden=self._forbidden)

        return {'p': portsp, 'a': portsa, 'n': portsn}

    def get_prev(self):
        return self.get_all['p']

    def get_actual(self):
        return self.get_all['a']

    def get_next(self):
        return self.get_all['n']

    def __str__(self):
        res = ''
        banner = "N\tPrev\t\tActu\t\tNext\n"
        res += (banner)
        res += ("-" * len(banner))
        res += "\n"

        ports = self.get_all()
        p = ports['p']
        a = ports['a']
        n = ports['n']

        for port in range(len(p)):
            res += ("%d\t%d\t\t%d\t\t%d\n" % (port, p[port], a[port], n[port]))
        res += ("-" * len(banner))
        res += "\n"

        return res

# TODO https://github.com/ldx/python-iptables
# TODO https://docs.python.org/3/library/argparse.html
def main():

    slot = 30

    secret = totp.gen_secret()

    print("Secret: %s" % secret)

    ports = TocTocPorts(secret, slot)

    print(ports)

    time.sleep(ports.next())

    while 1:
        print(ports)

        time.sleep(slot)


if __name__ == '__main__':
    main()
