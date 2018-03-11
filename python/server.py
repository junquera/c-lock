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
        self._actual = 0


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

import socket # TODO Reemplazar por https://docs.python.org/2/library/asyncore.html ? Por el método accept
import threading

class KnockablePort():

    def __init__(self, socket, next_port):
        self._socket = socket
        self._next_port = next_port

    def get_next_port(self):
        return self._next_port

    def get_socket(self):
        return self._socket


class PortManager():

    def __init__(self, ttp):
        self._ttp = ttp
        self._sockets = []

    def wait_and_listen(self, kp):
        # TODO ASYNC - asyncio
        s = kp.get_socket()
        p = s.getsockname()
        next_port = kp.get_next_port()

        while 1:
            try:
                sock, addr = s.accept()
                self.notify_connection(p, addr, next_port)
                sock.close()
            except:
                pass

    def notify_connection(self, p, addr, next_port):
        # TODO Open firewall some seconds. If next_port == 0, open result
        print("New connection to %d from %s, next step %d" %(p[1], addr[0], next_port))

    def open_socket(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', port))
            s.listen(5)
            return s
        except socket.error as e:
            if e.errno == 98:
                print("Error. El puerto %d ya está siendo utilizado por otro proceso" % port)
            raise e

    def open(self):
        self._ports = self._ttp.get_actual()
        print("Abriendo")

        n = self._ports.next()

        if n:
            # TODO Open the port until ttp.timeout
            pass

        while n:
            port = n
            n = self._ports.next()

            print("Opening %d" % port)

            s = self.open_socket(port)

            kp = KnockablePort(s, n)

            self._sockets.append(kp)
            threading.Thread(target=self.wait_and_listen, args=(kp,)).start()

    def close_socket(self, s):
        try:
            s.close()
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(s.getsockname())
        except:
            pass

    def close(self):
        # TODO Close firewall
        while len(self._sockets):
            kp = self._sockets.pop()
            s = kp.get_socket()
            print("Closing %d" % s.getsockname()[1])
            self.close_socket(s)

    def reset(self):
        self.close()
        self.open()

# https://eli.thegreenplace.net/2011/12/27/python-threads-communication-and-stopping
# http://www.bogotobogo.com/python/Multithread/python_multithreading_Event_Objects_between_Threads.php
class PortManagerWorker(threading.Thread):
    pass


class FirewallManager():
    pass

# TODO https://github.com/ldx/python-iptables
# TODO https://docs.python.org/3/library/argparse.html
# TODO https://twistedmatrix.com/trac/ || https://docs.python.org/3/library/signal.html
def main():

    slot = 30

    secret = totp.gen_secret()

    # TODO Delete after debug
    secret = '874895c82728d55c3e8e62c449954e1c2ee8d364f3bc953e230c23be452def7119b3c59d4be21799'
    print("Secret: %s" % secret)

    ttp = TocTocPorts(secret)

    pm = PortManager(ttp)

    # fwm = FirewallManager()

    while 1:
        pm.open()
        print("Abierto")
        time.sleep(ttp.next())
        pm.close()
        print("Cerrado")

if __name__ == '__main__':
    main()
