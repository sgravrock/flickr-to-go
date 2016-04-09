import unittest
import json
from mock import Mock, call
from containers import download_collections, download_set_list


class MockFlickrApi:
    def __init__(self):
        self.collections = MockFlickrCollections()
        self.photosets = MockFlickrSets()

class MockFlickrCollections:
    def configure(self, tree):
        result = json.dumps({'stat': 'ok', 'collections': tree})
        self.getTree = Mock(return_value=result)

class MockFlickrSets:
    def configure(self, pages):
        self.getList = Mock(side_effect=lambda **kwargs: \
                json.dumps(pages[kwargs['page'] - 1]))

class MockFileStore:
    def __init__(self):
        self.save_json = Mock()


class TestDownloadCollections(unittest.TestCase):
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
        self.flickr = MockFlickrApi()
        self.flickr.collections.configure(self.tree)

    def test_fetches(self):
        result = download_collections(MockFileStore(), self.flickr)
        self.flickr.collections.getTree.assert_has_calls([
                call(format='json', nojsoncallback=1)])
        self.assertEqual(result, self.tree)

    def test_saves(self):
        file_store = MockFileStore()
        result = download_collections(file_store, self.flickr)
        file_store.save_json.assert_called_with('collections.json', self.tree)


def build_sets_response(sets):
    return {
        'stat': 'ok',
        'photosets': {
            'photoset': sets
        }
    }


class TestDownloadSetList(unittest.TestCase):
    def setUp(self):
      #  { "photosets": { "cancreate": 1, "page": 1, "pages": 17, "perpage": 3, "total": 50,
   # "photoset": [
    #] }, "stat": "ok" }
        self.sets = [
            { "id": "1", "secret": "2" },
            { "id": "3", "secret": "4" },
            { "id": "5", "secret": "6" }
        ]
        self.page_size = 2
        page1 = build_sets_response(self.sets[0:2])
        page2 = build_sets_response(self.sets[2:3])
        self.flickr = MockFlickrApi()
        self.flickr.photosets.configure([page1, page2])

    def test_fetches(self):
        result = download_set_list(MockFileStore(), self.flickr, self.page_size)
        self.flickr.photosets.getList.assert_has_calls([
            call(page=1, per_page=2, format='json', nojsoncallback=1),
            call(page=2, per_page=2, format='json', nojsoncallback=1)
        ])
        self.assertEqual(result, self.sets)

    def test_saves(self):
        file_store = MockFileStore()
        download_set_list(file_store, self.flickr, self.page_size)
        file_store.save_json.assert_called_with('sets.json', self.sets)
