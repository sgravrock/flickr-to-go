import unittest
from mock import Mock, call
import photo
import json

class MockRequests:
    def __init__(self):
        self.contents = {}

    def get(self, url):
        if url not in self.contents:
            raise Exception('Un-mocked URL: ' + url)
        return MockResponse(self.contents[url])

class MockResponse:
    def __init__(self, content):
        self.content = content

class TestPhoto(unittest.TestCase):
    def test_download_originals(self):
        photos = [
                {'id': '25461030990', 'url_o': 'https://farm2.staticflickr.com/1521/25461030990_3621f6ae2d_o.jpg'},
                {'id': '23793491473', 'url_o': 'https://farm2.staticflickr.com/1514/23793491473_11cf9041b4_o.jpg'}
        ]
        responses = [
                '\xff\xd8\xff\xe1\x16&Exif\x00\x00II*\x00\x08\x00\x00\x00',
                '\xff\xd8\xff\xe1\x16&Exif\x00\x00II*\x00\x08\x00\x00\x01'
        ]
        requests = MockRequests()

        for i in xrange(0, len(photos)):
            requests.contents[photos[i]['url_o']] = responses[i]

        file_store = Mock()
        photo.download_originals(photos, file_store, requests)
        file_store.save_image.assert_has_calls([
                call('originals/25461030990_o.jpg', responses[0]),
                call('originals/23793491473_o.jpg', responses[1])])
