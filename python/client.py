from ttp import TocTocPorts
import socket

def toc_ports(ttp):

    values = ttp.get_actual()

    retry = 0
    n = values.next()
    while n:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(('localhost', n))
            s.close()
        except:
            if retry > 3:
                print("End")
                return
            retry += 1
            time.sleep(0.1)
            continue
        retry = 0
        n = values.next()
        print("Next %d" % n)

    print("Opening port %d" % ttp.get_destination())

def main():

    secret = '874895c82728d55c3e8e62c449954e1c2ee8d364f3bc953e230c23be452def7119b3c59d4be21799'

    print("Secret: %s" % secret)

    ports = TocTocPorts(secret)

    toc_ports(ports)

if __name__ == '__main__':
    main()
