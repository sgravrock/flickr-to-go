import unittest
from mock import Mock, call
import photo
import json
from StringIO import StringIO

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

class MockFlickrApi:
    def __init__(self, photo_infos):
        self.photos = MockFlickrPhotos(photo_infos)

class MockFlickrPhotos:
    def __init__(self, photo_infos):
        side_effect = lambda **kwargs: \
                json.dumps(photo_infos[kwargs['photo_id']])
        self.getInfo = Mock(side_effect=side_effect)


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
        file_store.exists.return_value = False
        photo.download_originals(photos, file_store, requests, StringIO())
        file_store.save_image.assert_has_calls([
                call('originals/25461030990_o.jpg', responses[0]),
                call('originals/23793491473_o.jpg', responses[1])])

    def test_download_originals_skips_existing(self):
        photos = [{'id': '25461030990', 'url_o': 'https://farm2.staticflickr.com/1521/25461030990_3621f6ae2d_o.jpg'}]
        requests = Mock()
        file_store = Mock()
        file_store.exists.return_value = True
        photo.download_originals(photos, file_store, requests, StringIO())
        self.assertEqual(requests.get.call_count, 0)

    def test_download_info(self):
        photos = [
            {'id': '1'},
            {'id': '2'}
        ]
        responses = {
            '1': { "photo": { "id": "1", "secret": "s1" }, "stat": "ok" },
            '2': { "photo": { "id": "2", "secret": "s2" }, "stat": "ok" }
        }
        file_store = Mock()
        photo.download_info(photos, file_store, MockFlickrApi(responses),
                StringIO())
        file_store.save_json.assert_has_calls([
            call('photo-info/1.json', responses['1']['photo']),
            call('photo-info/2.json', responses['2']['photo'])
        ])
