import threading
import uuid
import logging

log = logging.getLogger(__name__)

def bypass(fa, fb):

    def mix(*args, **kwargs):
        fa(*args, **kwargs)
        fb(*args, **kwargs)

    return mix

class ProcWorker(threading.Thread):

    def __init__(self, i_q, o_q):
        super(ProcWorker, self).__init__()
        self._id = uuid.uuid4()
        print(self._id)
        self._i = i_q
        self._o = o_q
        self._end_evt = threading.Event()

    def run(self):
        while not self._end_evt.is_set():
            evt = self._i.get(True)
            if evt:
                self.process_evt(evt)


    def process_evt(self, evt):
        # TODO Send received event!
        if evt.get_id() == ProcWorkerEvent.END:
            log.debug("Received close signal")
            self._end_evt.set()
            self._i.put(None)


class Broker(ProcWorker):

    _client_qs = []

    def __init__(self, i_q, o_q):
        super(Broker, self).__init__(i_q, o_q)
        self._client_qs.append(o_q)

    def add_client(self, client_q):
        self._client_qs.append(client_q)

    def process_evt(self, evt):
        super(Broker, self).process_evt(evt)

        for q in self._client_qs:
            q.put(evt)


class Event():

    def __init__(self, id, value):
        self._id = id
        self._value = value

    def get_value(self):
        return self._value

    def get_id(self):
        return self._id

    def __str__(self):
        return "EVENT %s - %s" % (self._id, self._value )

#-----------------------#

class ProcWorkerEvent():

    NONE = -1
    END = uuid.uuid4().bytes


class PortManagerEvent():

    NEW_CONNECTION = uuid.uuid4().bytes
    CLOSING_SOCKET = uuid.uuid4().bytes
    FIRST_PORT = uuid.uuid4().bytes
    LAST_PORT = uuid.uuid4().bytes
    ERROR_OPENING_SOCKET = uuid.uuid4().bytes
    PROTECT_PORT = uuid.uuid4().bytes

class TocTocPortsEvent():

    NEW_SLOT = uuid.uuid4().bytes
    LAST_PORT = uuid.uuid4().bytes
    PROTECT_PORT = uuid.uuid4().bytes


class FirewallManagerEvent():

    NEW_CONNECTION = uuid.uuid4().bytes
