import clockngpn.totp as totp
from clockngpn.proc_worker import Event, Broker, ProcWorkerEvent
from clockngpn.ttp import TocTocPorts, TocTocPortsWorker
from queue import Queue
import time
import os
import logging

from clockngpn.bidi import OTPBidi

import signal
import argparse

log = logging.getLogger(__name__)


def check_environment():

    if not os.geteuid() == 0:
        raise Exception("This program needs root for managing IPTABLES!")

    try:
        import iptc
    except Exception as _:

        if 'XTABLES_LIBDIR' not in os.environ:
            os.environ['XTABLES_LIBDIR'] = '/usr/lib/x86_64-linux-gnu/xtables'
        else:
            raise Exception("Error, la variable XTABLES_LIBDIR está mal configurada")


# TODO Sacar a una clase y hacer el main con arg_parser
def main_server(secret, slot, address, ports, opened):

    try:
        check_environment()
    except Exception as e:
        log.error(e)
        exit(-1)

    log.debug("Secret: %s" % secret)

    from clockngpn.port_manager import PortManagerWorker, PortManager
    from clockngpn.firewall_manager import FirewallManager, FirewallManagerWorker

    oq = Queue()
    bq = Queue()

    b = Broker(bq, oq)

    fwmq = Queue()
    b.add_client(fwmq)
    fwm = FirewallManager()
    fwmw = FirewallManagerWorker(fwmq, bq, fwm=fwm)

    for port in opened:
        fwm.open(port)

    pmq = Queue()
    b.add_client(pmq)
    pm = PortManager(address, unmanaged_ports=opened)
    pmw = PortManagerWorker(pmq, bq, pm=pm)

    ttpq = Queue()
    b.add_client(ttpq)
    ttp = TocTocPorts(secret, destination=ports)
    ttpw = TocTocPortsWorker(ttpq, bq, ttp)

    fwmw.start()
    pmw.start()
    ttpw.start()
    b.start()

    # TODO Refactor de este método
    def end(signum, *args):
        log.warning('Signal handler called with signal %s' % signum)
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
    signal.signal(signal.SIGSEGV, end)
    signal.signal(signal.SIGFPE, end)
    signal.signal(signal.SIGABRT, end)
    signal.signal(signal.SIGBUS, end)
    signal.signal(signal.SIGILL, end)
    # TODO Clase orquestador


def main():

    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
        'QUIET': logging.NOTSET
    }

    parser = argparse.ArgumentParser(description='Launch TOTP based port knocking protection')
    parser.add_argument('-ts', '--time-slot', dest='slot', default=30, type=int, help='Time slot for TOTP')
    parser.add_argument('-a', '--address', default='0.0.0.0', help="Address to protect")
    parser.add_argument('-s', '--secret', help="Secret part of TOTP")
    parser.add_argument('-p', '--protected-ports', type=int, default=[], action='append', help="Port which has to be protected")
    parser.add_argument('-o', '--opened-ports', type=int, default=[], action='append', help="Port which should be opened")
    parser.add_argument('--gen-secret', help="Generate random secret", action='store_true')
    parser.add_argument('--clean-firewall', help="Clean firewall configuration (e.g., after a bad close)", action='store_true')
    parser.add_argument('--log-level', default="DEBUG", help="Log level")
    # parser.add_argument('--config-file')

    args = parser.parse_args()

    log_level = args.log_level

    level = log_levels.get(log_level, logging.DEBUG)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if args.clean_firewall:

        try:
            check_environment()
        except Exception as e:
            log.error(e)
            exit(-1)

        from clockng.firewall_manager import FirewallManager

        FirewallManager().clean_firewall()

    elif args.gen_secret:

        i_secret = totp.gen_secret()

        otp_bidi = OTPBidi(i_secret)

        print("TOTP generated secret: %s" % i_secret)
        print(otp_bidi.generate())

    elif args.secret:
        i_secret = args.secret

        try:
            secret = totp.web_secret_2_bytes(i_secret)
        except Exception as e:
            log.error("Bad secret: Remember secret must be b32")
            return

        slot = args.slot

        address = args.address
        ports = args.protected_ports if args.protected_ports else []

        opened = args.opened_ports

        main_server(secret, slot, address, ports, opened)


    else:
        log.error("A secret is required to start")
        parser.print_help()
        return

if __name__ == '__main__':
    main()
