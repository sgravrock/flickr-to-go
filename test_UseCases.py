import os
import unittest
import tempfile
import shutil
import json
from StringIO import StringIO
from main import flickr_to_go
from mock_requests import MockRequests
from mock import Mock, patch
from StubFlickr import StubFlickrBuilder

@patch('main.authenticate')
class TestUseCases(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.environ["FLICKR_API_KEY"] = "whatever"
        os.environ["FLICKR_API_SECRET"] = "whatever"

    def tearDown(self):
        shutil.rmtree(self.dir)

    def assertSucceeded(self, result, output):
        if not result:
            self.assertEqual('', output.getvalue())
            self.fail()

    def assertFile(self, relative_path, expected_contents):
        with open(os.path.join(self.dir, relative_path)) as f:
            self.assertEqual(expected_contents, f.read())

    def test_downloads_original_photos(self, authenticate):
        authenticate.return_value = "anything truthy"
        flickr_builder = StubFlickrBuilder()
        photos = [
            {'id': '25461030990', 'url_o': 'https://example.com/a.jpg'},
            {'id': '24420214365', 'url_o': 'https://exampele.com/b.jpg'}
        ]
        contents = [
            '\xff\xd8\xff\xe1\x16&Exif\x00\x00II*\x00\x08\x00\x00\x00',
            '\xff\xd8\xff\xe1\x16&Exif\x00\x00II*\x00\x08\x00\x00\x01'
        ]
        flickr_builder.photo(photos[0], contents[0])
        flickr_builder.photo(photos[1], contents[1])
        flickr_api = flickr_builder.build_flickr_api()
        requests = flickr_builder.build_requests()

        with patch('main.flickr', new=flickr_api):
            with patch('main.requests', new=requests):
                output = StringIO()
                ok = flickr_to_go(self.dir, False, "key", "secret", output)
                self.assertSucceeded(ok, output)
                self.assertFile('originals/25461030990_o.jpg', contents[0])
                self.assertFile('originals/24420214365_o.jpg', contents[1])

