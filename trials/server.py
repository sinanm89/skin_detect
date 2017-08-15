from twisted.application import internet
from twisted.web import server
from skinny.server import SkinnyRpc

from twisted.internet import reactor


def main():
    root = SkinnyRpc()
    site = server.Site(root)
    reactor.listenTCP(8000, site)
    # return internet.TCPServer(8000, site)
    reactor.run()

if __name__ == '__main__':
    main()