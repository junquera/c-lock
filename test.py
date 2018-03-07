import asyncore, socket
import uuid
# https://docs.python.org/2/library/asyncore.html

class EchoServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.id = uuid.uuid4()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print ('[%s] Incoming connection from %s' % (self.id, repr(addr)))
            sock.close()

server = EchoServer('localhost', 8080)
print("Hey!")
server.serve_forever()
print("Ho!")
