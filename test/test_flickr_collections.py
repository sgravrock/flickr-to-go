import unittest
import json
from mock import Mock, call
import flickr_collections


class MockFlickrApi:
    def __init__(self, tree):
        self.collections = MockFlickrCollections(tree)

class MockFlickrCollections:
    def __init__(self, tree):
        result = json.dumps({'stat': 'ok', 'collections': tree})
        self.getTree = Mock(return_value=result)

class MockFileStore:
    def __init__(self):
        self.save_json = Mock()


class TestFlickrCollections(unittest.TestCase):
    def setUp(self):
        self.tree = {
            "collection": [
                {
                    "id": "1", "title": "Places",
                    "set": [
                        { "id": "123", "title": "a", "description": "" },
                        { "id": "456", "title": "b", "description": "" },
                    ]
                }
            ]
        }
        self.flickr = MockFlickrApi(self.tree)

    def test_download_fetches(self):
        result = flickr_collections.download(MockFileStore(), self.flickr)
        self.flickr.collections.getTree.assert_has_calls([
                call(format='json', nojsoncallback=1)])
        self.assertEqual(result, self.tree)

    def test_download_saves(self):
        file_store = MockFileStore()
        result = flickr_collections.download(file_store, self.flickr)
        file_store.save_json.assert_called_with('collections.json', self.tree)
