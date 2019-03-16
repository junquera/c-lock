from .ttp import TocTocPorts, gen_ports_from_pin
from . import totp
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

def toc_ports(values, address):

    for value in values:

        touch(address, value)

        time.sleep(0.2)

    log.debug("Knock finished")
