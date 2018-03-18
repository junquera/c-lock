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

        self.backup()

        log.debug("Starting FirewallManager")

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
        # TODO Evitar insertar reglas repetidas
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

        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
        rule = iptc.Rule()
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "toc-toc-ssh")
        chain.delete_rule(rule)

        chain = iptc.Chain(table, "toc-toc-ssh")
        chain.flush()
        chain.delete()

        chain = iptc.Chain(table, "toc-toc-ssh-reject")
        chain.flush()
        chain.delete()

        #TODO Delete chains

        self.restore()

    def backup(self):
        # TODO Search how to backup iptables
        pass

    def restore(self):
        # TODO Search how to restore iptables
        pass



class RuleManager(threading.Thread):

    stay_running = True
    rules = {}

    def __init__(self, fwm):
        super(RuleManager, self).__init__()
        self._lock = threading.Lock()
        self._fwm = fwm
        self.start()

    def run(self):
        while self.stay_running:
            print("Step")
            self.delete_caduced_rules()
            time.sleep(1)

    def close(self):
        self.stay_running = False
        self.delete_all_rules()

    def lock(f):

        def locker(self, *args, **kwargs):

            self._lock.acquire()

            res = f(self, *args, **kwargs)

            self._lock.release()

            return res

        return locker

    @lock
    def add_rule(self, r, caducity=-1):

        rule_id = str(uuid.uuid4())
        log.debug("Adding rule %s -> %s" % (rule_id, str(r)))

        self.rules[rule_id] = {
            'rule': r,
            'timestamp': time.time(),
            'caducity': caducity
        }

        return rule_id

    @lock
    def get_rule(self, rule_id):

        rule_data = self.rules.get(rule_id, None)

        return rule_data

    @lock
    def delete_rule(self, rule_id):

        if rule_id in self.rules:
            rule_data = self.rules[rule_id]
            try:
                log.debug("Deleting rule %s -> %s" % (rule_id, str(rule_data.get('rule'))))
                self._fwm.delete_rule(rule_data.get('rule'))
            except Exception as e:
                        print("Error deleting %s: %s" % (rule_id, str(e)))

            self.rules[rule_id] = None

    def delete_caduced_rules(self):
        keys = self.rules.keys()

        for rule_id in keys:
            rule_data = self.get_rule(rule_id)
            if rule_data:
                print(rule_data)
                print(((time.time() - rule_data['timestamp'])))
                if rule_data['caducity'] < 0:
                    continue
                elif rule_data['caducity'] < ((time.time() - rule_data['timestamp'])):
                    self.delete_rule(rule_id)

    def delete_all_rules(self):
        keys = self.rules.keys()
        for rule_id in keys:
            self.delete_rule(rule_id)

class FirewallManagerWorker(ProcWorker):


    def __init__(self, i_q, o_q, fwm=None):

        super(FirewallManagerWorker, self).__init__(i_q, o_q)

        if not fwm:
            fwm = FirewallManager()

        self._fwm = fwm

        # TODO Abrir puertos marcados como no gestionados (prohibidos)
        self._rule_manager = RuleManager(fwm)

    def process_evt(self, evt):

        super(FirewallManagerWorker, self).process_evt(evt)

        if evt.get_id() == ProcWorkerEvent.END:
            self._rule_manager.close()
            self._fwm.close()

        if evt.get_id() == PortManagerEvent.NEW_CONNECTION:
            evt_value = evt.get_value()
            port = evt_value['next']
            addr = evt_value['address']
            log.info("Opening port %s for %s" % (port, addr))
            r = self._fwm.open_port(port, origin=addr)
            self._rule_manager.add_rule(r, caducity=2)

        if evt.get_id() == TocTocPortsEvent.LAST_PORT:
            evt_value = evt.get_value()
            port = evt_value['port']
            addr = evt_value['address']
            log.info("Opening last port %s for %s" % (port, addr))
            r = self._fwm.open_port(port, origin=addr)
            self._rule_manager.add_rule(r, caducity=30)

        if evt.get_id() == PortManagerEvent.FIRST_PORT:
            evt_value = evt.get_value()
            port = evt_value['port']
            log.info("Opening first port %s" % (port))
            r = self._fwm.open_port(port)
            self._rule_manager.add_rule(r)


        if evt.get_id() == TocTocPortsEvent.NEW_SLOT:
            # TODO ¿Close o borrar las reglas guardadas?
            # self._fwm.close()
            self._rule_manager.delete_all_rules()
