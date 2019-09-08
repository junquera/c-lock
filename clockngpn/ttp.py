from .proc_worker import ProcWorker, Event, PortManagerEvent, TocTocPortsEvent
from . import totp
import time
import threading
import logging

log = logging.getLogger(__name__)


# 0 <= val < 1000000 --> 6 digits (24 bytes)
# 1024 < port < 10240
# 3 <= n_ports <= 6
def gen_ports_from_pin(pin, n_ports):

    values = []

    min_port = 2**10 # 1024
    max_port = 2**16 # 65536

    for i in range(n_ports):
        aux = totp.hotp(K=pin.to_bytes(3, byteorder='big'), I=i)
        r = int(((aux/1e6) * (max_port - min_port)) + min_port)
        values.append(r)

    return values


class PortList():

    def __init__(self, l):
        self._l = l
        self._actual = 0

    def actual(self):
        return self._l[self._actual]

    def get_values(self):
        return self._l

    def reset(self):
        self._actual = 0


class TocTocPorts():

    def __init__(self, secret, slot=30, n_ports=4, destination=[]):

        self._secret = secret
        self._slot = slot

        self._destination = destination

        if n_ports < 1:
            raise Exception("Error, at least %d ports needed" % 1)

        if n_ports > 10:
            raise Exception("Error, max ports: %d" % 10)

        self._n_ports = n_ports

        self._ports = self.get_actual()

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


    def get_actual(self):

        tca = self.last()
        vala = totp.totp(self._secret, tca)
        portsa = gen_ports_from_pin(vala, self._n_ports)

        return PortList(portsa)

    # def __str__(self):
    #     def row(values):
    #         return "| " + ("{:<15}| "*len(values)).format(*values) + "\n"
    #
    #     res = ''
    #     banner = row(["N", "Prev", "Actu", "Next"]) # "N\tPrev\t\tActu\t\tNext\n"
    #     res += ("-" * (len(banner) - 2))
    #     res += "\n"
    #     res += (banner)
    #     res += ("-" * (len(banner) - 2))
    #     res += "\n"
    #
    #     ports = self.get_all()
    #     p = ports['p'].get_values()
    #     a = ports['a'].get_values()
    #     n = ports['n'].get_values()
    #
    #     for port in range(len(p)):
    #         res += (row((port, p[port], a[port], n[port])))
    #     res += ("-" * (len(banner) - 2))
    #     res += "\n"
    #
    #     res += " [*] NEXT_SLOT: %ds\n" % self.next()
    #     return res


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
            self._o.put(Event(TocTocPortsEvent.LAST_PORT, {'ports': self._ttp.get_destination(), 'address': evt.get_value()['address']}))
