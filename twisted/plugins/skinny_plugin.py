"""Skinny plugin command for twistd."""
from twisted.web import server
from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from skinny.server import SkinnyRpc


class Options(usage.Options):

    """
    Options for the twistd -n skinny plugin.

    Example:
        twistd -n skinny -p 1234
        twistd -n skinny --port=1234
    """

    optParameters = [["port", "p", 8000, "The port number to listen on."]]


class SkinnyServiceMaker(object):

    """Create a Jsonrpc server on port 8000."""

    implements(IServiceMaker, IPlugin)
    tapname = "skinny"
    description = "A jsonrpc server that will detect nudity" \
                  " in images given to it by the urls"
    options = Options

    def makeService(self, options):
        """
        Start a JsonRpc Server on a defined port.

        Args:
            options: Options object provided by the class Options.
        """
        root = SkinnyRpc()
        site = server.Site(root)
        return internet.TCPServer(int(options['port']), site)


serviceMaker = SkinnyServiceMaker()
