"""skinny Client test script"""
from twisted.internet import reactor, defer
from txjsonrpc.web.jsonrpc import Proxy


def printValue(value):
    print "Response:"
    print value


def printError(error):
    print error


def shutDown(data):
    print "Shutting down reactor..."
    reactor.stop()


proxy = Proxy('http://127.0.0.1:8000/')
test_image_url = "http://i.imgur.com/XgbIBkhl.jpg"

d = proxy.callRemote('skin_score', test_image_url)
d.addCallbacks(printValue, printError).addCallback(shutDown)

defer.DeferredList([d])

reactor.run()