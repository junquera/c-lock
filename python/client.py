from ttp import TocTocPorts
import socket
import time

import logging

log = logging.getLogger(__name__)

def toc_ports(ttp, address):

    values = ttp.get_actual()

    retry = 0
    n = values.next()
    while n:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            print("Connection to %d" % n)
            s.connect((address, n))
            s.close()
        except:
            if retry > 3:
                log.error("Max retries! Port %d doesnt work" % n)
                return
            retry += 1
            time.sleep(retry * 0.1)
            continue
        retry = 0
        n = values.next()
        log.debug("Next %d" % n)
        time.sleep(0.2)

    log.debug("Opening port %d" % ttp.get_destination())

import argparse
def main():

    parser = argparse.ArgumentParser(description='Launch TOTP based port knocking protection')
    parser.add_argument('-ts', '--time-slot', dest='slot', default=30, type=int, help='Time slot for TOTP')
    parser.add_argument('-a', '--address', default='127.0.0.1', help="Address to knock")
    parser.add_argument('-s', '--secret', help="Secret part of TOTP", required=True)
    args = parser.parse_args()

    secret = args.secret
    address = args.address

    log.debug("Secret: %s" % secret)

    ports = TocTocPorts(secret)
    print(ports)
    toc_ports(ports, address)

if __name__ == '__main__':
    main()
