# -*- test-case-name: skinny.tests.test_server -*-
"""Test scenarios for skinny module."""
from mock import Mock, patch
import os
from twisted.internet import defer
from twisted.trial import unittest
from skinny.faults import InvalidImageUrl
from skinny.server import SkinnyRpc
from skinny.skin_detect import skin_detect_percentage, nudity_detect_certainty
from skinny.utils import get_image_from_url

TEST_BASE = os.path.dirname(os.path.abspath(__file__))
TEST_IMAGE_DIR = os.path.join(TEST_BASE, 'images')
PROCESSED_DIR = os.path.join(TEST_BASE, 'processed')
TEST_IMAGE_NAME = 'test_image1.jpg'


class RpcTestCase(unittest.TestCase):

    """Test class for classes in server.py."""

    def test_faults(self):
        """Test to see if faults are being generated."""
        some_fault = InvalidImageUrl()
        self.assertTrue(some_fault.faultString is not None)

    @patch("skinny.server.deferToThread")
    @patch("skinny.server.get_image_from_url")
    def test_nudity_score_method(self, get_image_from_url, deferToThread):
        """Check nudity method."""
        skinny_obj = SkinnyRpc()
        file = Mock()
        file.name = "irrelevant"
        get_image_from_url.return_value = defer.succeed(file)
        deferToThread.return_value = defer.succeed(0.5)
        nudity_response = skinny_obj.jsonrpc_nudity_score('some_url')
        self.assertTrue(type(nudity_response.result == dict))

    @patch("skinny.server.deferToThread")
    @patch("skinny.server.get_image_from_url")
    def test_skin_score_method(self, get_image_from_url, deferToThread):
        """Check nudity method."""
        skinny_obj = SkinnyRpc()
        file = Mock()
        file.name = "irrelevant"
        get_image_from_url.return_value = defer.succeed(file)
        deferToThread.return_value = defer.succeed(0.5)
        nudity_response = skinny_obj.jsonrpc_skin_score('some_url')
        self.assertTrue(type(nudity_response.result == dict))


class UtilsTestCase(unittest.TestCase):

    """Test class for classes in server.py."""

    def test_image_url(self):
        """Test to see if faults are being generated."""
        wrong_html = 'invalid url inside'
        failed_deferred = get_image_from_url(wrong_html)
        self.assertFailure(failed_deferred, InvalidImageUrl)

    @patch("skinny.utils.treq")
    def test_treq_response_code(self, treq):
        """Check treq response code for non 200 codes."""
        response = Mock()
        response.code = 404
        treq.get.return_value = defer.succeed(response)
        bad_status_url = 'http://badstatus.com'
        failed_deferred = get_image_from_url(bad_status_url)
        self.assertFailure(failed_deferred, InvalidImageUrl)

    @patch("skinny.utils.treq")
    def test_image_type(self, treq):
        """Check image type support."""
        response = Mock()
        response.code = 200
        treq.get.return_value = defer.succeed(response)
        bad_status_url = 'http://correct_image.com/image.WRONGTYPE'
        failed_deferred = get_image_from_url(bad_status_url)
        self.assertFailure(failed_deferred, InvalidImageUrl)

    @patch("skinny.utils.treq")
    @patch.dict("skinny.utils.__dict__", {"TEMP_DIR": "temp"})
    def test_image_create(self, treq):
        """Check image creation."""
        response = Mock()
        response.code = 200
        treq.get.return_value = defer.succeed(response)
        correct_url = 'http://correct_image.com/temporary_image.jpg'
        treq.collect.return_value = defer.succeed(None)
        deferred = get_image_from_url(correct_url)
        self.assertTrue(type(deferred.result) == file)


class SkinDetectTestCase(unittest.TestCase):

    """Test class for classes in skin_detect.py."""

    @patch.dict("skinny.skin_detect.__dict__",
                {"PROCESSED_DIR": "nudity_processed"})
    def test_nudity_score(self):
        """Check for an expected return value for nudity_score_url function."""
        test_image_file = os.path.join(TEST_IMAGE_DIR, TEST_IMAGE_NAME)
        result = nudity_detect_certainty(image_dir=test_image_file)
        self.assertTrue(0 <= result <= 1)

    @patch.dict("skinny.skin_detect.__dict__",
                {"PROCESSED_DIR": "skin_processed"})
    def test_skin_score(self):
        """Check for an expected return value for skin_score_url function."""
        test_image_file = os.path.join(TEST_IMAGE_DIR, TEST_IMAGE_NAME)
        result = skin_detect_percentage(image_dir=test_image_file)
        self.assertTrue(0 <= result <= 1)
