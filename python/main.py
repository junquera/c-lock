import totp
import time
import codecs

def get_time(slot_size):
    t = int(time.time())
    remainder = t % slot_size

    t -= remainder

    return t

def next_slot_at(slot_size):
    t = int(time.time())
    remainder = t % slot_size

    return slot_size - remainder


def bytes2int(b):
    return int.from_bytes(b, byteorder='big', signed=False)

forbidden = [8080, 8081]

# 1 < n < 10
def gen_ports(val, n=3):
    values = []
    for i in range(n):
        aux = bytes2int(val[2*i:(2*i)+2])
        if aux < 1024:
            aux += 1024
        while aux in forbidden or aux in values:
            aux+=1
        values.append(aux)
    return values

class ConfPorts():

    ports = []

    def __init__(self):
        pass

    def put(self, p):
        if len(self.ports) >= 3:
            self.ports = self.ports[1:]
        self.ports.append(p)

    def get_all(self):
        return self.ports

    def get_prev(self):
        return self.ports[0]

    def get_actual(self):
        return self.ports[1]

    def get_next(self):
        return self.ports[2]

    def __str__(self):
        res = ''
        banner = "N\tPrev\t\tActu\t\tNext\n"
        res += (banner)
        res += ("-" * len(banner))
        res += "\n"

        p = self.ports[0]
        a = self.ports[1]
        n = self.ports[2]

        for port in range(len(p)):
            res += ("%d\t%d\t\t%d\t\t%d\n" % (port, p[port], a[port], n[port]))
        res += ("-" * len(banner))
        res += "\n\n"

        return res

def main():

    slot = 30

    secret = totp.gen_secret()

    print("Secret: %s" % secret)

    ports = ConfPorts()

    tc = get_time(slot)
    tcp = tc - slot
    tcn = tc + slot

    valp = totp.totp(secret, tcp)
    vala = totp.totp(secret, tc)
    valn = totp.totp(secret, tcn)

    portsp = gen_ports(valp, n=4)
    portsa = gen_ports(vala, n=4)
    portsn = gen_ports(valn, n=4)

    ports.put(portsp)
    ports.put(portsa)
    ports.put(portsn)

    print(ports)

    ns = next_slot_at(slot)
    print("Next slot at %ds..." % ns)
    time.sleep(ns)

    while 1:
        tcn = get_time(slot) + slot
        valn = totp.totp(secret, tcn)
        portsn = gen_ports(valn, n=4)
        ports.put(portsn)

        print(ports)

        time.sleep(slot)


if __name__ == '__main__':
    main()
