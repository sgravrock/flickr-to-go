import unittest
from mock import Mock, call
import photolist
import json

class MockFlickrApi:
    def __init__(self, photos_return_values):
        self.people = MockFlickrPeople(photos_return_values)

class MockFlickrPeople:
    def __init__(self, photos_return_values):
        side_effect = lambda **kwargs: \
                photos_return_values[kwargs['page'] - 1]
        self.getPhotos = Mock(side_effect=side_effect)


class MockFileStore:
    def __init__(self):
        self.save_json = Mock()

def build_photos_response(photolist):
    return json.dumps({'photos': {'photo': photolist}})



class TestPhotoList(unittest.TestCase):
    def setUp(self):
        self.photos = [
            {"id": "25461030990","owner": "21041082@N02","secret": "x",
                "server": "1521","farm": 2,"title": "","ispublic": 1,
                "isfriend": 0, "isfamily": 0},
            {"id": "24420214365","owner": "21041082@N02","secret": "x",
                "server": "1704","farm": 2,"title": "15th & Leary",
                "ispublic": 1,"isfriend": 0,"isfamily": 0 },
            {"id": "23793491473","owner": "21041082@N02","secret": "y",
                "server": "1514","farm": 2,
                "title": "Occidental and Jackson", "ispublic": 1,
                "isfriend": 0,"isfamily": 0}
        ]
        self.page_size = 2
        page1 = build_photos_response(self.photos[0:2])
        page2 = build_photos_response(self.photos[2:3])
        self.flickr = MockFlickrApi([page1, page2])

    def test_download_fetches(self):
        result = photolist.download(MockFileStore(), self.flickr,
                self.page_size)
        self.flickr.people.getPhotos.assert_has_calls([
                call(page=1, per_page=2, user_id='me', extras='url_o',
                    format='json', nojsoncallback=1),
                call(page=2, per_page=2, user_id='me', extras='url_o',
                    format='json', nojsoncallback=1)])
        self.assertEqual(result, self.photos)

    def test_download_saves(self):
        file_store = MockFileStore()
        photolist.download(file_store, self.flickr, self.page_size)
        file_store.save_json.assert_called_with('photos.json', self.photos)
