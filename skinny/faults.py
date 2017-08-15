"""Custom Fault classes for RPC server responses."""
from txjsonrpc.jsonrpclib import Fault, INVALID_METHOD_PARAMS


class InvalidImageUrl(Fault):

    """Custom Error for invalid image url header."""

    faultCode = INVALID_METHOD_PARAMS

    def __init__(self, *args, **kwargs):
        """Set the faultString to the one provided."""
        default_msg = 'Error during image download. Check url and image.'
        self.faultString = kwargs.get('faultString', default_msg)
