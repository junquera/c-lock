from proc_worker import ProcWorker, Event, bypass, ProcWorkerEvent, PortManagerEvent, TocTocPortsEvent
from ttp import TocTocPortsWorker
from port_manager import PortManagerWorker
import uuid
import logging
import threading
import time
import iptc

import os

log = logging.getLogger(__name__)

# GUIDE: https://github.com/ldx/python-iptables
class FirewallManager():

    def __init__(self):

        table = iptc.Table(iptc.Table.FILTER)

        # Crear chain
        try:
            table.create_chain("toc-toc-ssh")
        except:
            log.debug("toc-toc-ssh exists!")

        # Crear última chain
        try:
            table.create_chain("toc-toc-ssh-reject")
        except:
            log.debug("toc-toc-ssh-reject exists!")

        # TODO Las reglas que tenemos que borrar al terminar con *
        # Apuntar INPUT a toc-toc-ssh
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "toc-toc-ssh")
        chain.insert_rule(rule)

        # Our chain
        chain = iptc.Chain(table, "toc-toc-ssh")
        chain.flush()

        # Apuntar toc-toc-ssh a toc-toc-ssh-reject
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "toc-toc-ssh-reject")
        chain.insert_rule(rule)

        # Last chain!
        chain = iptc.Chain(table, "toc-toc-ssh-reject")
        chain.flush()

        # Drop all
        rule = iptc.Rule()
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "REJECT")
        chain.insert_rule(rule)

        # Accept all established
        rule = iptc.Rule()
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "ACCEPT")
        match = iptc.Match(rule, "state")
        match.state = "RELATED,ESTABLISHED"
        rule.add_match(match)
        chain.insert_rule(rule)

        # TODO Not working right
        # Accept all output connections
        # rule = iptc.Rule()
        # rule.protocol = "tcp"
        # rule.target = iptc.Target(rule, "ACCEPT")
        # rule.src = "127.0.0.1"
        # chain.insert_rule(rule)


    def open_port(self, port, origin=None):
        table = iptc.Table(iptc.Table.FILTER)

        chain = iptc.Chain(table, "toc-toc-ssh")

        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        if origin:
            rule.src = origin
        rule.dst = "127.0.0.1"
        match = iptc.Match(rule, "tcp")
        match.dport = "%d" % port
        rule.add_match(match)
        rule.target = iptc.Target(rule, "ACCEPT")
        chain.insert_rule(rule)

        return rule

    def close_port(self, port, origin=None):
        table = iptc.Table(iptc.Table.FILTER)

        chain = iptc.Chain(table, "toc-toc-ssh")

        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        if origin:
            rule.src = origin
        rule.dst = "127.0.0.1"
        match = iptc.Match(rule, "tcp")
        match.dport = "%d" % port
        rule.add_match(match)
        rule.target = iptc.Target(rule, "REJECT")
        chain.insert_rule(rule)

        return rule

    def delete_rule(self, rule):
        table = iptc.Table(iptc.Table.FILTER)

        chain = iptc.Chain(table, "toc-toc-ssh")
        chain.delete_rule(rule)

    def close(self):
        table = iptc.Table(iptc.Table.FILTER)
        chain = iptc.Chain(table, "toc-toc-ssh")
        chain.flush()

        # Apuntar toc-toc-ssh a toc-toc-ssh-reject
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "toc-toc-ssh-reject")
        chain.insert_rule(rule)


        self.restore()

    def backup(self):
        # TODO Search how to backup iptables

        pass

    def restore(self):
        # TODO Search how to restore iptables
        pass

class FirewallManagerWorker(ProcWorker):

    def __init__(self, i_q, o_q, fwm=FirewallManager()):

        super(FirewallManagerWorker, self).__init__(i_q, o_q)

        self._fwm = fwm

    def drop_rule(self, rule):
        try:
            self._fwm.delete_rule(rule)
        except Exception as e:
            log.debug("Error deleting rule %s: %s" % (str(rule), e))

    def drop_rule_timer(self, rule, time=2):
        threading.Timer(time, self.drop_rule, args=(rule,)).start()

    def process_evt(self, evt):
        super(FirewallManagerWorker, self).process_evt(evt)

        if evt.get_id() == ProcWorkerEvent.END:
            self._fwm.close()

        if evt.get_id() == PortManagerEvent.NEW_CONNECTION:
            evt_value = evt.get_value()
            port = evt_value['next']
            addr = evt_value['address']
            log.info("Opening port %s for %s" % (port, addr))
            r = self._fwm.open_port(port, origin=addr)
            threading.Thread(target=self.drop_rule_timer, args=(r,)).start()


        if evt.get_id() == TocTocPortsEvent.LAST_PORT:
            evt_value = evt.get_value()
            port = evt_value['port']
            addr = evt_value['address']
            log.info("Opening last port %s for %s" % (port, addr))
            r = self._fwm.open_port(port, origin=addr)
            threading.Thread(target=self.drop_rule_timer, args=(r,), kwargs={'time': 30}).start()

        if evt.get_id() == PortManagerEvent.FIRST_PORT:
            evt_value = evt.get_value()
            port = evt_value['port']
            log.info("Opening first port %s" % (port))
            r = self._fwm.open_port(port)
            # TODO Dejarlo abierto X tiempo o esperar al siguiente slot?
            # threading.Thread(target=self.drop_rule_timer, args=(r,), kwargs={'time': 30}).start()


        if evt.get_id() == TocTocPortsEvent.NEW_SLOT:
            # TODO ¿Close o borrar las reglas guardadas?
            self._fwm.close()
            port_list = evt.get_value()['port_list'].get_values()
