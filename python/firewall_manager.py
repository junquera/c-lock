import time
import iptc

# export XTABLES_LIBDIR=/usr/lib/x86_64-linux-gnu/xtables

# TODO https://github.com/ldx/python-iptables
class FirewallManager():

    chain_rules = {}

    def backup(self):

        table = iptc.Table(iptc.Table.FILTER)

        for chain in table.chains:
            if not chain.name in self.chain_rules:
                self.chain_rules[chain.name] = []

            for rule in chain.rules:
                self.chain_rules[chain.name].append(rule)
                chain.delete_rule(rule)

    def restore(self):

        table = iptc.Table(iptc.Table.FILTER)

        for cn in self.chain_rules:
            c = iptc.Chain(table, cn)

            for rule in self.chain_rules[cn]:
                c.insert_rule(rule)

        self.chain_rules = {}

fwm = FirewallManager()

# TODO Orden de chains en lugar de backup
# fwm.backup()

table = iptc.Table(iptc.Table.FILTER)


def bootstrap():

    # Crear chain
    try:
        table.create_chain("toc-toc-ssh")
    except:
        pass

    # Crear última chain
    try:
        table.create_chain("toc-toc-ssh-reject")
    except:
        pass

    try:

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
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "REJECT")
        chain.insert_rule(rule)

        # Accept all established
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "ACCEPT")
        match = iptc.Match(rule, "state")
        match.state = "RELATED,ESTABLISHED"
        rule.add_match(match)
        chain.insert_rule(rule)

        # Accept all output connections
        rule = iptc.Rule() # *
        rule.protocol = "tcp"
        rule.target = iptc.Target(rule, "ACCEPT")
        rule.src = "127.0.0.1"
        rule.add_match(match)
        chain.insert_rule(rule)

    except Exception as e:
        print(e)
        pass

def open_port(port, origin=None):
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

def delete_rule(rule):
    chain = iptc.Chain(table, "toc-toc-ssh")
    chain.delete_rule(rule)

bootstrap()
r = open_port(2424, origin="127.0.0.1")
time.sleep(20)
delete_rule(r)
