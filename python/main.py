import totp
import time
import codecs
def get_time(slot_size):
    t = int(time.time())
    remainder = t % slot_size

    t -= remainder

    return t


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

def main():

    secret = totp.gen_secret()

    print("Secret: %s" % secret)

    while 1:
        tc = get_time(30)
        tcp = tc - 30
        tcn = tc + 30

        val = totp.totp(secret, tc)
        valp = totp.totp(secret, tcp)
        valn = totp.totp(secret, tcn)

        ports = gen_ports(val, n=4)
        portsp = gen_ports(valp, n=4)
        portsn = gen_ports(valn, n=4)
        print("N\tPrev\t\tActu\t\tNext")
        for port in range(len(ports)):
            print("%d\t%d\t\t%d\t\t%d" % (port, portsp[port], ports[port], portsn[port]))
            pass
        time.sleep(5)


if __name__ == '__main__':
    main()
