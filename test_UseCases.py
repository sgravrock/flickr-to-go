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

#@patch('main.flickr_api')
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
        urls = [
            'https://farm2.staticflickr.com/1521/25461030990_3621f6ae2d_o.jpg',
            'https://farm2.staticflickr.com/1514/24420214365_11cf9041b4_o.jpg'
        ]
        responses = [
            '\xff\xd8\xff\xe1\x16&Exif\x00\x00II*\x00\x08\x00\x00\x00',
            '\xff\xd8\xff\xe1\x16&Exif\x00\x00II*\x00\x08\x00\x00\x01'
        ]
        flickr_builder.photolist([
            {'id': '25461030990', 'url_o': urls[0]},
            {'id': '24420214365', 'url_o': urls[1]}
        ])
        requests = MockRequests()
        requests.contents[urls[0]] = responses[0]
        requests.contents[urls[1]] = responses[1]

        with patch('main.flickr', new=flickr_builder.build()):
            with patch('main.requests', new=requests):
                output = StringIO()
                ok = flickr_to_go(self.dir, False, "key", "secret", output)
                self.assertSucceeded(ok, output)
                self.assertFile('originals/25461030990_o.jpg', responses[0])
                self.assertFile('originals/24420214365_o.jpg', responses[1])

        #requests = MockRequests()
        #with patch('photo.requests', new=requests) as mock_requests:
