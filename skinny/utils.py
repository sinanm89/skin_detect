"""Utilty script containing globals and useful functions for RPC server."""
import os
import treq
from twisted.internet import defer
from skinny.faults import InvalidImageUrl

SKINNY_BASE = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(SKINNY_BASE, 'temp')
PROCESSED_DIR = os.path.join(SKINNY_BASE, 'processed')
ERROR_MESSAGES = {
    "connection": "nodename nor servname provided, or not known.",
    "image_type": "Invalid Image Type. Image should be a .JPG/.JPEG or .PNG.",
    "image_header": "Header does not contain an image content-type.",
    "url": "Url returned invalid status_code: {}"
}
ACCEPTED_IMAGE_TYPES = ['jpg', 'jpeg', 'png']


@defer.inlineCallbacks
def get_image_from_url(image_url):
        """
        Download image into a temporary file.

        Creates the temp directory if it doesnt exist.

        TODO:
            - mongodb keep urls, downloaded image and
            processed image hashes
            - check downloaded image hash if same
                - return pre-processed image

        Args:
            image_url: A string for the image
        Returns:
            A Bool and a String which denote the success and path to file
            If the image_url is incorrect or it fails for some reason the Bool
            will be False and the String will be the error message.
            Example:
            True, "/Users/snn/Documents/projects/Scrunch/skinny/skinny/temp"
            False, "Header does not contain an image content-type"
        """
        if 'http' not in image_url:
            raise(InvalidImageUrl(faultString="Url invalid, http missing"))
        # treq doesnt accept unicode...
        image_url = image_url.encode('utf-8')
        response = yield treq.get(image_url)
        if not response.code == 200:
            raise(InvalidImageUrl(
                faultString=ERROR_MESSAGES['url'].format(response.code)))
        filename = image_url.split('/')[-1]
        file_type = filename.split('.')[-1]
        # check file type for accepted images
        if file_type not in ACCEPTED_IMAGE_TYPES:
            raise(InvalidImageUrl(faultString=ERROR_MESSAGES['image_type']))
        # check if temp file exists create if necessary
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        filename_dir = os.path.join(TEMP_DIR, filename)
        # open image file and start writing
        image_file = file(filename_dir, 'wb')
        yield treq.collect(response, image_file.write)
        image_file.close()
        defer.returnValue(image_file)
