from ttp import TocTocPorts, gen_ports_from_pin
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
    parser.add_argument('-s', '--secret', help="Secret part of TOTP")
    parser.add_argument('-p', '--pin', help="TOTP pin", type=int)
    args = parser.parse_args()

    address = args.address

    log.debug("Address: %s" % address)

    print("jaja")
    if args.secret:
        if args.pin:
            raise Exception("Error secret or pin, never both (scecret ^ pin)")
        secret = args.secret
        ports = TocTocPorts(secret)
        log.debug("Secret: %s" % secret)
    elif:
        pin = args.pin
        ports = gen_ports_from_pin(pin)
        log.debug("Pin: %d" % pin)
    else:
        raise Exception("Set secret or pin")


    toc_ports(ports, address)

if __name__ == '__main__':
    main()
