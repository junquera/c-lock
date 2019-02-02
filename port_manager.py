
import socket, sys
from struct import *
import threading
from proc_worker import ProcWorker, Event, bypass, ProcWorkerEvent, TocTocPortsEvent, PortManagerEvent

from client import touch

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

        try:
            self._s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

            evt = threading.Event()
            t = threading.Thread(target=self.wait_and_listen, args=(evt,))
            self._threads.append(evt)
            t.start()

        except socket.error:
            # TODO Send END
            print( 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    def wait_and_listen(self, evt):
        log.info("wait_and_listen")
        errors = 0
        # TODO Ver por qué no termina el hilo...
        while not evt.is_set():
            try:
                packet = self._s.recvfrom(65565)

                #packet string from tuple
                packet = packet[0]

                #take first 20 characters for the ip header
                ip_header = packet[0:20]
                # print(ip_header)

                #now unpack them :)
                iph = unpack('!BBHHHBBH4s4s' , ip_header)

                version_ihl = iph[0]
                version = version_ihl >> 4
                ihl = version_ihl & 0xF

                iph_length = ihl * 4

                ttl = iph[5]
                protocol = iph[6]
                s_addr = socket.inet_ntoa(iph[8])
                d_addr = socket.inet_ntoa(iph[9])

                # print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)

                tcp_header = packet[iph_length:iph_length+20]

                #now unpack them :)
                tcph = unpack('!HHLLBBHHH' , tcp_header)

                source_port = tcph[0]
                dest_port = tcph[1]
                sequence = tcph[2]
                acknowledgement = tcph[3]
                doff_reserved = tcph[4]

                flags = tcph[5]

                syn = flags & 0b10
                ack = flags & 0b10000
                fin = flags & 0b1

                # TODO If is start connection
                if syn and not ack:
                    self.notify_connection(s_addr, dest_port)

            except Exception as e:
                if not evt.is_set():
                    log.error("Error on socket: %s" % str(e))
                    errors += 1
                    if errors >= 3:
                        log.critical("Error on socket: %s" % str(e))
                        break

        log.info("nor_wait_nor_listen")

    def notify_connection(self, addr, port):
        # TODO Hacer esto con métodos con bloqueos (@lock)
        if addr in self._active:
            addr_info = self._active[addr]
            if port == addr_info['next']:
                next_n = addr_info['n'] + 1
                if len(self._port_list) <= next_n:
                    self.last_port(addr)
                    del self._active[addr]
                else:
                    addr_info['n'] = next_n
                    addr_info['next'] = self._port_list[next_n]
                    self._active[addr] = addr_info
            else:
                del self._active[addr]
        else:
            if self._port_list[0] == port:
                self._active[addr] = dict(next=self._port_list[1], n=1)

    def last_port(self, addr):
        log.info("%s reached last port" % (addr))

    def open(self, port_list):
        self._active = {}
        self._port_list = port_list

    def close_thread(self, evt):
        try:
            evt.set()
        except Exception as e:
            pass

    def unlock_threads(self):
        while len(self._threads):
            try:
                evt = self._threads.pop()
                self.close_thread(evt)
            except Exception as e:
                pass

    def close(self):
        self.unlock_threads()
        # Knock a port for stopping the socket thread
        touch(self._address, 12345)
        self._s.close()


# https://eli.thegreenplace.net/2011/12/27/python-threads-communication-and-stopping
# http://www.bogotobogo.com/python/Multithread/python_multithreading_Event_Objects_between_Threads.php
class PortManagerWorker(ProcWorker):

    def __init__(self, i_q, o_q, pm=None):
        super(PortManagerWorker, self).__init__(i_q, o_q)

        if not pm:
            pm = PortManager()

        self._pm = pm

        self._pm.notify_connection = bypass(self._pm.notify_connection, self.notify_connection)
        self._pm.last_port = bypass(self._pm.last_port, self.last_port)

    def notify_connection(self, addr, port):
        self._o.put(Event(PortManagerEvent.NEW_CONNECTION, {'port': port, 'address': addr}))

    def last_port(self, address):
            self._o.put(Event(PortManagerEvent.LAST_PORT, dict(address=address)))

    def process_evt(self, evt):
        super(PortManagerWorker, self).process_evt(evt)

        if evt.get_id() == ProcWorkerEvent.END:
            self._pm.close()

        if evt.get_id() == TocTocPortsEvent.NEW_SLOT:
            port_list = evt.get_value()['port_list'].get_values()
            self._pm.open(port_list)
