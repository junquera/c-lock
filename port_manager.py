import socket
import threading
from proc_worker import ProcWorker, Event, bypass, ProcWorkerEvent, TocTocPortsEvent, PortManagerEvent

import logging

log = logging.getLogger(__name__)


class KnockablePort():

    def __init__(self, socket, next_port):
        self._socket = socket
        self._next_port = next_port

    def get_next_port(self):
        return self._next_port

    def get_socket(self):
        return self._socket


class PortManager():

    def __init__(self, address='0.0.0.0'):
        self._sockets = []
        self._threads = []
        self._address = address

    def wait_and_listen(self, kp, evt):

        s = kp.get_socket()
        p = s.getsockname()
        next_port = kp.get_next_port()

        errors = 0
        # TODO Ver por qué no termina el hilo...
        while not evt.is_set():
            try:
                sock, addr = s.accept()
                self.notify_connection(p, addr, next_port)
                self.handle_connection(sock, addr)
            except Exception as e:
                if not evt.is_set():
                    log.error("Error on socket: %s" % str(e))
                    errors += 1
                    if errors >= 3:
                        log.critical("Error on socket: %s" % str(e))
                        break

        log.debug("Fin del thread del socket %s" % str(p))

    def handle_connection(self, sock, addr):
        sock.close()

    def notify_first_port(self, p):
        log.debug("First port: %d" % p)

    def notify_connection(self, p, addr, next_port):
        if next_port:
            log.debug("New connection to %d from %s, next step %d" %(p[1], addr[0], next_port))
        else:
            log.debug("New connection to %d from %s, open the result!" % (p[1], addr[0]))

    def notify_error_opening_socket(self):
        self.close()

    def open_socket(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((self._address, port))
            s.listen(5)
            return s
        except socket.error as e:
            if e.errno == 98:
                log.critical("El puerto %d ya está siendo utilizado por otro proceso" % port)
            else:
                log.critical("Error al abrir puerto %d: %s" % (port, e))

        return None

    def open(self, port_list):

        n = port_list.next()

        if n:
            self.notify_first_port(n)

        while n:
            port = n
            n = port_list.next()

            log.info("Opening %d" % port)

            s = self.open_socket(port)
            if s:
                kp = KnockablePort(s, n)
                self._sockets.append(kp)
                evt = threading.Event()
                t = threading.Thread(target=self.wait_and_listen, args=(kp, evt,))
                self._threads.append(evt)
                t.start()
            else:
                self.notify_error_opening_socket()
                break

    def notify_socket_closed(self, s_addr):
        log.debug("Closing socket on port %d" % (s_addr[1]))

    def close_socket(self, s):
        try:
            self.notify_socket_closed(s.getsockname())
            s.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            pass

    def close_thread(self, evt):
        try:
            evt.set()
        except:
            pass

    def unlock_threads(self):
        while len(self._threads):
            try:
                evt = self._threads.pop()
                self.close_thread(evt)
            except:
                pass

    def close_sockets(self):
        # Copy self._sockets
        while len(self._sockets):
            try:
                kp = self._sockets.pop()
                s = kp.get_socket()
                self.close_socket(s)
            except:
                pass

    def close(self):
        self.unlock_threads()
        self.close_sockets()

    def reset(self, port_list):
        self.close()
        self.open(port_list)


# https://eli.thegreenplace.net/2011/12/27/python-threads-communication-and-stopping
# http://www.bogotobogo.com/python/Multithread/python_multithreading_Event_Objects_between_Threads.php
class PortManagerWorker(ProcWorker):

    def __init__(self, i_q, o_q, pm=None):
        super(PortManagerWorker, self).__init__(i_q, o_q)

        if not pm:
            pm = PortManager()

        self._pm = pm

        self._pm.notify_socket_closed = bypass(self._pm.notify_socket_closed, self.notify_socket_closed)
        self._pm.notify_connection = bypass(self._pm.notify_connection, self.notify_connection)
        self._pm.notify_first_port = bypass(self._pm.notify_first_port, self.notify_first_port)
        self._pm.notify_error_opening_socket = bypass(self._pm.notify_error_opening_socket, self.notify_error_opening_socket)

    def notify_error_opening_socket(self):
        self._o.put(Event(PortManagerEvent.ERROR_OPENING_SOCKET, None))

    def notify_first_port(self, p):
        self._o.put(Event(PortManagerEvent.FIRST_PORT, {'port': p}))

    def notify_socket_closed(self, s_addr):
        self._o.put(Event(PortManagerEvent.CLOSING_SOCKET, {'port': s_addr[1]}))

    def notify_connection(self, p, addr, next_port):
        if next_port:
            self._o.put(Event(PortManagerEvent.NEW_CONNECTION, {'port': p[1], 'address': addr[0], 'next': next_port}))
        else:
            self._o.put(Event(PortManagerEvent.LAST_PORT, {'port': p[1], 'address': addr[0]}))

    def process_evt(self, evt):
        super(PortManagerWorker, self).process_evt(evt)

        if evt.get_id() == ProcWorkerEvent.END:
            self._pm.close()

        if evt.get_id() == TocTocPortsEvent.NEW_SLOT:
            self._pm.close()
            self._pm.open(evt.get_value()['port_list'])
