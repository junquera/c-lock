from proc_worker import ProcWorker, Event, PortManagerEvent, TocTocPortsEvent
import totp
import time
import uuid
import threading
import logging

log = logging.getLogger(__name__)

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
            return -1

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
            aux = totp.bytes2int(val[2*i:(2*i)+2])

            min_port = (2 << 10) + 1
            max_port = 2 << 13

            # Value between min_port and max_port, from 2^16 values
            aux = int(min_port + (max_port - min_port) * float(aux) / (2 << 16))

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

        return PortList(portsn)

    def __str__(self):
        def row(values):
            return "| " + ("{:<15}| "*len(values)).format(*values) + "\n"

        res = ''
        banner = row(["N", "Prev", "Actu", "Next"]) # "N\tPrev\t\tActu\t\tNext\n"
        res += ("-" * (len(banner) - 2))
        res += "\n"
        res += (banner)
        res += ("-" * (len(banner) - 2))
        res += "\n"

        ports = self.get_all()
        p = ports['p'].get_values()
        a = ports['a'].get_values()
        n = ports['n'].get_values()

        for port in range(len(p)):
            res += (row((port, p[port], a[port], n[port])))
        res += ("-" * (len(banner) - 2))
        res += "\n"

        res += " [*] NEXT_SLOT: %ds\n" % self.next()
        return res

class TocTocPortsWorker(ProcWorker):

    def __init__(self, i_q, o_q, ttp):
        super(TocTocPortsWorker, self).__init__(i_q, o_q)
        self._ttp = ttp
        threading.Thread(target=self.work).start()

    # TODO Cerrar este thread
    def work(self):

        while not self._end_evt.is_set():
            # TODO Tal vez no desde aquí, pero hay que lanzar un evento con los puertos reservados
            self._o.put(Event(TocTocPortsEvent.NEW_SLOT, {'port_list': self._ttp.get_actual()}))
            next_t = self._ttp.next()
            log.debug("Next slot in %ds" % next_t)
            self._end_evt.wait(next_t)

        log.debug("Fin del thread de TocTocPorts")

    def process_evt(self, evt):

        super(TocTocPortsWorker, self).process_evt(evt)

        if evt.get_id() == PortManagerEvent.LAST_PORT:
            self._o.put(Event(TocTocPortsEvent.LAST_PORT, {'port': self._ttp.get_destination(), 'address': evt.get_value()['address']}))
