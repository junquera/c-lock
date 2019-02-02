from ttp import TocTocPorts
import socket
import time

import logging

log = logging.getLogger(__name__)
logging.basicConfig(
    level= logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def touch(address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0)
    try:
        log.info("Touching %d" % port)
        s.connect((address, port))
        s.close()
    except Exception as e:
        pass

def toc_ports(ttp, address):

    values = ttp.get_actual()

    retry = 0
    n = values.next()
    while n:
        touch(address, n)

        retry = 0
        n = values.next()
        time.sleep(0.2)

    log.debug("Knock finished")

import argparse
def main():

    parser = argparse.ArgumentParser(description='Launch TOTP based port knocking protection')
    parser.add_argument('-ts', '--time-slot', dest='slot', default=30, type=int, help='Time slot for TOTP')
    parser.add_argument('-a', '--address', help="Address to knock", required=True)
    parser.add_argument('-s', '--secret', help="Secret part of TOTP", required=True)
    args = parser.parse_args()

    secret = args.secret
    address = args.address

    log.debug("Address: %s" % address)
    log.debug("Secret: %s" % secret)

    ports = TocTocPorts(secret)

    toc_ports(ports, address)

if __name__ == '__main__':
    main()
