import threading
from queue import Queue
import time

class Proc():

    def __init__(self):
        pass

    def a(self):
        print("A")

    def b(self):
        print("B")


class ProcWorker(threading.Thread):

    def __init__(self, i_q, o_q):
        super(ProcWorker, self).__init__()
        self.instance = Proc()
        self.i = i_q
        self.o = o_q

    def run(self):

        while 1:
            aob = self.i.get(True)
            time.sleep(1)
            if aob == 'a':
                self.instance.a()
                self.o.put('b')
            else:
                self.instance.b()
                self.o.put('a')

q1 = Queue()
q2 = Queue()

ProcWorker(q1, q2).start()
ProcWorker(q2, q1).start()
print("All running")

q2.put('b')
