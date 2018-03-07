import totp
import time

def bytes2int(b):
    return int.from_bytes(b, byteorder='big', signed=False)

# TODO Threading & sockets!
# import threading, socket

class Last(Exception):
    pass

class PortList():

    def __init__(self, l):
        self._l = l
        self.actual = 0


    def actual(self):
        return self._l[self._actual]

    def next(self):

        if len(self._l) <= self._actual:
            # raise Last()
            return 0

        n = self._l[self._actual]
        self._actual += 1
        return n

    def prev(self):

        if len(0 <= self._actual):
            raise Last()

        n = self._l[self._actual]
        self._actual -= 1
        return n

    def get_values(self):
        return self._l

    def reset(self):
        self._actual = 0


class TocTocPorts():

    def __init__(self, secret, slot=30, n_ports=4, destination=22, forbidden=[]):

        self._secret = secret
        self._slot = slot
        self._forbidden = forbidden
        self._destination = destination

        if n_ports > 20:
            raise Exception("Error, max ports: %d" % 20)

        self._n_ports = n_ports

        ports = self.get_all()

        self._p = ports['p']
        self._a = ports['a']
        self._n = ports['n']
        # time.sleep(ns)

    # 1 < n < 10
    def gen_ports(self, val):
        values = []
        for i in range(self._n_ports):
            aux = bytes2int(val[2*i:(2*i)+2])
            if aux < 1024:
                aux += 1024
            while aux in self._forbidden or aux in values or aux == self._destination:
                aux += 1
            values.append(aux)
        return values


    def get_slot(self):
        return self._slot

    def get_destination(self):
        return self._destination

    def next(self):
        t = int(time.time())
        remainder = t % self._slot
        return self._slot - remainder


    def last(self):
        t = int(time.time())
        remainder = t % self._slot

        return t - remainder

    def get_all(self):
        return {'p': self.get_prev(), 'a': self.get_actual(), 'n': self.get_next()}

    def get_prev(self):

        tcp = self.last() - self._slot
        valp = totp.totp(self._secret, tcp)
        portsp = self.gen_ports(valp)

        return PortList(portsp)

    def get_actual(self):

        tca = self.last()
        vala = totp.totp(self._secret, tca)
        portsa = self.gen_ports(vala)

        return PortList(portsa)

    def get_next(self):

        tcn = self.last() + self._slot
        valn = totp.totp(self._secret, tcn)
        portsn = self.gen_ports(valn)

        return portsn

    def __str__(self):
        res = ''
        banner = "N\tPrev\t\tActu\t\tNext\n"
        res += (banner)
        res += ("-" * len(banner))
        res += "\n"

        ports = self.get_all()
        p = ports['p'].get_values()
        a = ports['a'].get_values()
        n = ports['n'].get_values()

        for port in range(len(p)):
            res += ("%d\t%d\t\t%d\t\t%d\n" % (port, p[port], a[port], n[port]))
        res += ("-" * len(banner))
        res += "\n"

        return res

def manage_socket(s, next):
    pass

import socket
import threading

def open_ports(ttp):

    ss = []
    try:
        ttp_next = ttp.next()
        t0 = time.time()

        values = ttp.get_actual()

        '''
        TODO
        1.- Abrir todos los puertos.
        2.- Al escuchar recibir petición en puerto n, abrir puerto n+1 a esa IP.
            2.1.- Abrir cada puerto (excepto el primero) durante 2 segundos.
        3.- Al terminar, abrir (también durante 2 segundos) el puerto final a la IP.
        4.- Si antes de este proceso se termina ttp.next, cerrar todo y volver a empezar.
        '''

        n = values.next()
        while n and time.time() - t0 < ttp_next:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ss.append(s)
            s.bind(('0.0.0.0', n))
            s.listen(1)

            # TODO ASYNC BLOCK?
            s.settimeout(ttp_next - (time.time() - t0))
            s.accept()
            s.close()
            # ASYNC BLOCK

            n = values.next()
            print("Next %d" % n)

        print("Opening port %d" % ttp.get_destination())
    except Exception as e:
        for s in ss:
            try:
                s.close()
            except:
                pass
        pass

import asyncio

class PortManager():

    def __init__(self, ttp):
        self._ttp = ttp
        self._sockets = []
        self.open()

    def open(self):
        self._ports = self._ttp.get_actual()
        print("Abriendo")
        for port in self._ports.get_values():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sockets.append(s)
            print("Opening %d" % port)
            s.bind(('0.0.0.0', port))
            s.listen(1)

            # TODO ASYNC - asyncio
            p = s.getsockname()[1]
            while 1:
                sock, addr = s.accept()
                print("New connection to %d from %s" %(p, addr))
                sock.close()

    def close(self):
        while len(self._sockets):
            s = self._sockets.pop()
            print("Closing %d" % s.port)
            try:
                s.close()
            except:
                pass

    def reset(self):
        self.close()
        self.open()

class FirewallManager():
    pass

# TODO https://github.com/ldx/python-iptables
# TODO https://docs.python.org/3/library/argparse.html
# TODO https://twistedmatrix.com/trac/
def main():

    slot = 30

    secret = totp.gen_secret()

    print("Secret: %s" % secret)

    ttp = TocTocPorts(secret)

    pm = PortManager(ttp)

    # fwm = FirewallManager()

    while 1:
        pm.open()
        time.sleep(ttp.next())
        pm.close()

if __name__ == '__main__':
    main()
