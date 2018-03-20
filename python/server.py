import totp
from proc_worker import Event, Broker, ProcWorkerEvent
from ttp import *
from queue import Queue
import time
import os
import logging

import signal

log = logging.getLogger(__name__)



# TODO Sacar a una clase y hacer el main con arg_parser
def main_server(secret, slot, forbidden):


    slot = slot

    secret = secret

    forbidden = forbidden

    log.debug("Secret: %s" % secret)

    if not os.geteuid() == 0:
        log.error("This program needs root for managing IPTABLES!")
        return -1

    try:
        import iptc
    except:

        if 'XTABLES_LIBDIR' not in os.environ:
            os.environ['XTABLES_LIBDIR'] = '/usr/lib/x86_64-linux-gnu/xtables'
        else:
            raise "Error, la variable XTABLES_LIBDIR está mal configurada"

    from port_manager import PortManagerWorker, PortManager
    from firewall_manager import FirewallManager, FirewallManagerWorker

    oq = Queue()
    bq = Queue()

    b = Broker(bq, oq)

    fwm = FirewallManager()
    fwmq = Queue()
    b.add_client(fwmq)
    fwmw = FirewallManagerWorker(fwmq, bq, open_ports=forbidden, fwm=fwm)

    pmq = Queue()
    b.add_client(pmq)
    pm = PortManager()
    pmw = PortManagerWorker(pmq, bq, pm=pm)

    ttp = TocTocPorts(secret, forbidden=forbidden)

    ttpq = Queue()
    b.add_client(ttpq)
    ttpw = TocTocPortsWorker(ttpq, bq, ttp)

    # TODO Refactor de este método
    def end(*args):
        bq.put(Event(ProcWorkerEvent.END, None))
        retry = 0
        while retry <= 3:
            if not fwmw.is_alive() and not pmw.is_alive() and not ttpw.is_alive() and not b.is_alive():
                break
            time.sleep(retry * 1)

        if fwmw.is_alive():
            log.warning("Bad killing thread fwmw")
        if pmw.is_alive():
            log.warning("Bad killing thread pmw")
        if ttpw.is_alive():
            log.warning("Bad killing thread ttpw")
        if b.is_alive():
            log.warning("Bad killing thread broker")

        if fwmw.is_alive() or pmw.is_alive() or ttpw.is_alive() or b.is_alive():
            exit(0)


    signal.signal(signal.SIGINT, end)
    # TODO Clase orquestador

import argparse

def main():
    # secret abc123
    # listen_address 0.0.0.0

    parser = argparse.ArgumentParser(description='Launch TOTP based port knocking protection')
    parser.add_argument('-ts', '--time-slot', dest='slot', default=30, type=int, help='Time slot for TOTP')
    parser.add_argument('-f', '--forbidden', default=[], type=int, nargs='+', help="Ports already in use or not manageable (space separated)")
    parser.add_argument('-a', '--address', default='0.0.0.0', help="Address to protect")
    parser.add_argument('-s', '--secret', help="Secret part of TOTP")
    parser.add_argument('-p', '--protected-port', type=int, help="Port which has to be protected")
    parser.add_argument('--gen-secret', help="Generate random secret", action='store_true')
    parser.add_argument('--log-level', default="DEBUG", help="Log level")
    args = parser.parse_args()

    log_level = args.log_level
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
        'QUIET': logging.NOTSET
    }

    logging.basicConfig(
        level=log_levels.get(log_level, logging.DEBUG),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    if args.gen_secret:
        secret = totp.gen_secret()
        print("Secret: %s" % secret)
        args.secret = secret

    if not args.secret:
        parser.print_help()
        return

    main_server(args.secret, args.slot, args.forbidden)

if __name__ == '__main__':
    main()
