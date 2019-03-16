from tts.ttp import TocTocPorts, gen_ports_from_pin
import tts.totp
from tts.client import toc_ports
import socket
import time

import logging

log = logging.getLogger(__name__)
logging.basicConfig(
    level= logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

import argparse
def main():

    parser = argparse.ArgumentParser(description='Launch TOTP based port knocking protection')
    parser.add_argument('-ts', '--time-slot', dest='slot', default=30, type=int, help='Time slot for TOTP')
    parser.add_argument('-a', '--address', help="Address to knock", required=True)
    parser.add_argument('-s', '--secret', help="Secret part of TOTP")
    parser.add_argument('-p', '--pin', type=int, help="TOTP pin")
    parser.add_argument('-n', '--ports', type=int, help="Number of ports configured", default=4)
    args = parser.parse_args()

    address = args.address

    log.debug("Address: %s" % address)
    n_ports = args.ports

    if args.secret:

        if args.pin:
            raise Exception("Error secret or pin, never both (scecret ^ pin)")

        try:
            secret = totp.web_secret_2_bytes(args.secret)
        except Exception as e:
            log.error("Bad secret: Remember secret = b32(secret_bytes)")
            return

        ports = TocTocPorts(secret).get_actual().get_values()
        log.debug("Secret: %s" % secret)
    elif args.pin:
        pin = args.pin
        ports = gen_ports_from_pin(pin, n_ports)
        log.debug("Pin: %d" % pin)
    else:
        raise Exception("Set secret or pin")


    toc_ports(ports, address)

if __name__ == '__main__':
    main()
