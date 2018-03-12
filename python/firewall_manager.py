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
fwm.backup()

table = iptc.Table(iptc.Table.FILTER)



# TODO Comprobar si existe chain
# TODO Order chain
try:
    table.create_chain("toc-toc-ssh")
except:
    pass

chain = iptc.Chain(table, "toc-toc-ssh")

rule = iptc.Rule()

rule.protocol = "tcp"
rule.src = "127.0.0.1"

match = iptc.Match(rule, "tcp")
match.dport = "2424"
rule.add_match(match)

# match = iptc.Match(rule, "iprange")
# # match.src_range = "127.0.0.1-127.0.0.2"
# rule.add_match(match)

rule.target = iptc.Target(rule, "DROP")

# rule.protocol = "tcp"
# m.dport = 22

# t = rule.create_target("ACCEPT")
# t = rule.create_target("DROP")
# t.to_ports = "22"

chain.insert_rule(rule)

fwm.restore()

print("Disabled")
time.sleep(30)

chain.delete_rule(rule)
