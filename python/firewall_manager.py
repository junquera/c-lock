import time
import iptc

# TODO https://github.com/ldx/python-iptables
class FirewallManager():

    pass



table = iptc.Table(iptc.Table.FILTER)
chain = iptc.Chain(table, "toc-toc-ssh")

rule = iptc.Rule()
rule.src = "127.0.0.1"
rule.protocol = "tcp"

# m = rule.create_match("tcp")
# m.dport = 22

# t = rule.create_target("ACCEPT")
t = rule.create_target("DROP")
t.to_ports = "22"
rule.target = t

chain.insert_rule(rule)

time.sleep(5)

chain.delete_rule(rule)
