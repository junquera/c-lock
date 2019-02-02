from proc_worker import ProcWorker, ProcWorkerEvent, PortManagerEvent, TocTocPortsEvent
import uuid
import logging
import threading
import time
import iptc


log = logging.getLogger(__name__)


# GUIDE: https://github.com/ldx/python-iptables
class FirewallManager():

    def __init__(self):

        self.backup()

        log.debug("Starting FirewallManager")

        table = iptc.Table(iptc.Table.FILTER)

        # Crear chain
        try:
            table.create_chain("toc-toc-ssh-unmanaged")
        except Exception as e:
            log.debug("toc-toc-ssh-unmanaged exists!")

        # Crear chain
        try:
            table.create_chain("toc-toc-ssh")
        except Exception as e:
            log.debug("toc-toc-ssh exists!")

        # Crear última chain
        try:
            table.create_chain("toc-toc-ssh-reject")
        except Exception as e:
            log.debug("toc-toc-ssh-reject exists!")

        # TODO ¿Debería venir desde ACCEPT?
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        # Apuntar INPUT a toc-toc-ssh-unmanaged
        rule.target = iptc.Target(rule, "toc-toc-ssh-unmanaged")
        chain.insert_rule(rule,position=len(chain.rules))


        # toc-toc-ssh-unmanaged config
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "toc-toc-ssh-unmanaged")
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "toc-toc-ssh")
        chain.insert_rule(rule)

        # Accept all established
        rule = iptc.Rule()
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "ACCEPT")
        match = iptc.Match(rule, "state")
        match.state = "RELATED,ESTABLISHED"
        rule.add_match(match)
        chain.insert_rule(rule)

        # TODO Add option to block also this connections
        # Accept all localhost connections
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        rule.src = "127.0.0.1"
        rule.target = iptc.Target(rule, "ACCEPT")
        chain.insert_rule(rule)

        # toc-toc-ssh config
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "toc-toc-ssh")
        # Apuntar toc-toc-ssh a toc-toc-ssh-reject
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "toc-toc-ssh-reject")
        chain.insert_rule(rule)

        # Last chain!
        chain = iptc.Chain(table, "toc-toc-ssh-reject")

        # Drop all
        rule = iptc.Rule()
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "REJECT")
        chain.insert_rule(rule)


        # TODO Not working right
        # Accept all output connections
        # rule = iptc.Rule()
        # rule.protocol = "tcp"
        # rule.target = iptc.Target(rule, "ACCEPT")
        # rule.src = "127.0.0.1"
        # chain.insert_rule(rule)
    #
    # def unmanage_port(self, port):
    #
    #     table = iptc.Table(iptc.Table.FILTER)
    #
    #     chain = iptc.Chain(table, "toc-toc-ssh-unmanaged")
    #
    #     rule = iptc.Rule() # *
    #     rule.protocol = "tcp"
    #     match = iptc.Match(rule, "tcp")
    #     match.dport = "%d" % port
    #     rule.add_match(match)
    #
    #     # TODO Debería ir a INPUT, pero puede hacer un bucle infinito
    #     rule.target = iptc.Target(rule, "ACCEPT")
    #
    #     chain.insert_rule(rule)

    def open_port(self, port, s_address=None):
        # TODO Evitar insertar reglas repetidas
        table = iptc.Table(iptc.Table.FILTER)

        chain = iptc.Chain(table, "toc-toc-ssh")

        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        if s_address:
            rule.src = s_address
        # rule.dst = "0.0.0.0"
        match = iptc.Match(rule, "tcp")
        match.dport = "%d" % port
        rule.add_match(match)
        rule.target = iptc.Target(rule, "ACCEPT")

        # TODO Puede servir para evitar repetidos
        # try:
        #     self.delete_rule(rule)
        # except Exception as e:
        #     pass

        chain.insert_rule(rule)

        return rule

    def gen_rule(self, port, s_address=None):

        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        if s_address:
            rule.src = s_address
        # rule.dst = "0.0.0.0"
        match = iptc.Match(rule, "tcp")
        match.dport = "%d" % port
        rule.add_match(match)
        rule.target = iptc.Target(rule, "ACCEPT")

        return rule

    def close_port(self, port, s_address=None):
        table = iptc.Table(iptc.Table.FILTER)

        chain = iptc.Chain(table, "toc-toc-ssh")

        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        if s_address:
            rule.src = s_address
        # rule.dst = "0.0.0.0"
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

    def clean_firewall(self):
        log.info("Cleaning firewall rules")

        table = iptc.Table(iptc.Table.FILTER)

        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
        rule = iptc.Rule()
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "toc-toc-ssh-unmanaged")

        while rule in chain.rules:
            chain.delete_rule(rule)

        chain = iptc.Chain(table, "toc-toc-ssh-unmanaged")
        chain.flush()
        chain.delete()

        chain = iptc.Chain(table, "toc-toc-ssh")
        chain.flush()
        chain.delete()

        chain = iptc.Chain(table, "toc-toc-ssh-reject")
        chain.flush()
        chain.delete()


    def close(self):
        self.clean_firewall()
        self.restore()

    def backup(self):
        # TODO Search how to backup iptables
        pass

    def restore(self):
        # TODO Search how to restore iptables
        pass



# TODO Pasar ar ProcWorker
class RuleManager(threading.Thread):

    rules = {}

    def __init__(self, fwm):
        super(RuleManager, self).__init__()
        self._lock = threading.Lock()
        self._fwm = fwm
        self._end_evt = threading.Event()
        self.start()

    def run(self):
        while not self._end_evt.is_set():
            self.delete_caduced_rules()
            self._end_evt.wait(1)

    def close(self):
        self._end_evt.set()
        self.delete_all_rules()

    def lock(f):

        def locker(self, *args, **kwargs):

            self._lock.acquire()

            res = f(self, *args, **kwargs)

            self._lock.release()

            return res

        return locker

    @lock
    def add_rule(self, r, caducity=-1, protected=False):

        # TODO rule_id como hash de la regla para evitar repetidos
        # Sin repetidos, sólo actualizaríamos la caducidad
        rule_id = str(uuid.uuid4())
        log.debug("Adding rule %s -> %s" % (rule_id, str(r)))

        # TODO Comprobar si ya existe
        self.rules[rule_id] = {
            'rule': r,
            'timestamp': time.time(),
            'caducity': caducity,
            'protected': protected
        }

        return rule_id

    @lock
    def exist_rule(self, r):

        for rule in self.rules:
            raux = self.rules[rule]
            if raux['rule'] == r:
                return rule

        return None

    @lock
    def renew_rule_timestamp(self, rule_id, caducity=None):

        if caducity:
            self.rules[rule_id]['caducity'] = caducity

        self.rules[rule_id]['timestamp'] = time.time()

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
                log.error("Error deleting %s: %s" % (rule_id, str(e)))

            del self.rules[rule_id]

    def delete_caduced_rules(self):
        # Copy of keys
        keys = [key for key in self.rules.keys()]

        for rule_id in keys:
            rule_data = self.get_rule(rule_id)
            if rule_data:
                if rule_data['caducity'] < 0:
                    continue
                elif rule_data['caducity'] < ((time.time() - rule_data['timestamp'])):
                    self.delete_rule(rule_id)

    # If `hard`, the protected rules are deleted too
    def delete_all_rules(self, hard=False):

        keys = [key for key in self.rules.keys()]

        for rule_id in keys:
            rule_data = self.get_rule(rule_id)
            if rule_data:
                # Delete if its not protected or hard deleting
                if hard or not rule_data['protected']:
                    self.delete_rule(rule_id)


class FirewallManagerWorker(ProcWorker):

    def __init__(self, i_q, o_q, fwm=None):

        super(FirewallManagerWorker, self).__init__(i_q, o_q)

        if not fwm:
            fwm = FirewallManager()

        self._fwm = fwm

        # TODO Abrir puertos marcados como no gestionados (prohibidos)
        self._rule_manager = RuleManager(fwm)

    def open_port(self, port, s_address=None, caducity=-1, protected=False):
        # We protect this rule for allowing the user to connect on step change
        r = self._fwm.gen_rule(port, s_address=s_address)
        exist = self._rule_manager.exist_rule(r)
        if exist:
            self._rule_manager.renew_rule_timestamp(exist)
        else:
            try:
                self._fwm.open_port(port, s_address=s_address)
                self._rule_manager.add_rule(r, caducity=caducity, protected=protected)
                log.debug("Opening port %d for %s" % (port, s_address))
            except Exception as e:
                log.critical("Error opening port %d: %e" % (port, e))

    def process_evt(self, evt):

        super(FirewallManagerWorker, self).process_evt(evt)

        if evt.get_id() == ProcWorkerEvent.END:
            self._rule_manager.close()
            self._fwm.close()

        if evt.get_id() == TocTocPortsEvent.LAST_PORT:
            evt_value = evt.get_value()
            ports = evt_value['ports']
            addr = evt_value['address']
            log.info("Opening ports %s for %s" % (ports, addr))

            for port in ports:
                self.open_port(port, s_address=addr, caducity=30, protected=True)

        if evt.get_id() == TocTocPortsEvent.NEW_SLOT:
            # TODO ¿Close o borrar las reglas guardadas?
            # self._fwm.close()
            self._rule_manager.delete_all_rules()
