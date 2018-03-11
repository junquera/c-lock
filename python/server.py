import totp
from proc_worker import Event, Broker
from ttp import *
from queue import Queue
from port_manager import *
from port_manager import PortManagerWorker

import logging

log = logging.getLogger(__name__)


class FirewallManager():
    # TODO https://github.com/ldx/python-iptables
    pass


def main():

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    slot = 30

    secret = totp.gen_secret()

    # TODO Delete after debug
    secret = '874895c82728d55c3e8e62c449954e1c2ee8d364f3bc953e230c23be452def7119b3c59d4be21799'
    log.debug("Secret: %s" % secret)

    oq = Queue()
    bq = Queue()

    b = Broker(bq, oq)

    pmq = Queue()
    b.add_client(pmq)
    pm = PortManagerWorker(pmq, bq)

    ttp = TocTocPorts(secret)

    ttpq = Queue()
    b.add_client(ttpq)
    ttpw = TocTocPortsWorker(ttpq, bq, ttp)
    # fwm = FirewallManager()

if __name__ == '__main__':
    main()
