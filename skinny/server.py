"""Module with class that determines skin percentage."""
from twisted.internet import defer
from twisted.internet.threads import deferToThread
from skinny.skin_detect import skin_detect_percentage
from utils import get_image_from_url
from txjsonrpc.web import jsonrpc


class SkinnyRpc(jsonrpc.JSONRPC):

    """
    This class measures the percentage of skin from an image.

    Example json data:
        {'method': 'nudity_score',
        'params': {'image_url' : 'http://i.imgur.com/XgbIBkhl.jpg'}}
    """

    addSlash = True

    @defer.inlineCallbacks
    def jsonrpc_nudity_score(self, image_url):
        """
        Measure the nudity of the image of a given url.

        Args:
            image_url: url of an image must be jpg, jpeg or png otherwise
            returns a Fault

        Returns:
            A dict with key 'nudity_certainty' that depicts the nudity
            probability
        """
        image_file = yield get_image_from_url(image_url)
        nudity_certainty = yield deferToThread(skin_detect_percentage,
                                               image_file.name)
        defer.returnValue({'nudity_certainty': nudity_certainty})

    @defer.inlineCallbacks
    def jsonrpc_skin_score(self, image_url):
        """
        Measure the amount of skin in the image of a  given url.

        Args:
            image_url: url of an image must be jpg, jpeg or png otherwise
            returns a Fault

        Returns:
            A dict with key 'skin_percentage' that depicts the percentage
            of skin in the image
        """
        image_file = yield get_image_from_url(image_url)
        skin_percentage = yield deferToThread(skin_detect_percentage,
                                              image_file.name)
        defer.returnValue({'skin_percentage': skin_percentage})
