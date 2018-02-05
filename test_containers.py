import unittest
import json
import urllib2
from httplib import BadStatusLine
from mock import Mock, call, patch
from StringIO import StringIO
from containers import download_collections, download_set_list, download_set_photolists
from download import FlickrApiDownloader, ErrorHandler


class MockFlickrApi:
    def __init__(self):
        self.collections = MockFlickrCollections()
        self.photosets = MockFlickrSets()

class MockFlickrCollections:
    def configure(self, tree):
        result = json.dumps({'stat': 'ok', 'collections': tree})
        self.getTree = Mock(return_value=result)

class MockFlickrSets:
    def configure_set_list(self, pages):
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
        downloader = FlickrApiDownloader(MockFileStore(), Mock())
        result = download_collections(downloader, self.flickr)
        self.flickr.collections.getTree.assert_has_calls([
                call(format='json', nojsoncallback=1)])
        self.assertEqual(result, self.tree)

    def test_saves(self):
        file_store = MockFileStore()
        downloader = FlickrApiDownloader(file_store, Mock())
        result = download_collections(downloader, self.flickr)
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
        self.sets = [
            { 'id': '1', 'secret': '2' },
            { 'id': '3', 'secret': '4' },
            { 'id': '5', 'secret': '6' }
        ]
        self.page_size = 2
        page1 = build_sets_response(self.sets[0:2])
        page2 = build_sets_response(self.sets[2:3])
        self.flickr = MockFlickrApi()
        self.flickr.photosets.configure_set_list([page1, page2])

    def test_fetches(self):
        downloader = FlickrApiDownloader(MockFileStore(), Mock())
        result = download_set_list(downloader, self.flickr, self.page_size)
        self.flickr.photosets.getList.assert_has_calls([
            call(page=1, per_page=2, format='json', nojsoncallback=1),
            call(page=2, per_page=2, format='json', nojsoncallback=1)
        ])
        self.assertEqual(result, self.sets)

    def test_saves(self):
        file_store = MockFileStore()
        downloader = FlickrApiDownloader(file_store, Mock())
        download_set_list(downloader, self.flickr, self.page_size)
        file_store.save_json.assert_called_with('sets.json', self.sets)


class TestDownloadSets(unittest.TestCase):
    def test_simple(self):
        sets = [
            { 'id': '1', 'secret': '2' },
            { 'id': '3', 'secret': '4' }
        ]
        end_response = { 'stat': 'fail', 'code': 1 }
        responses = {
            '1': {
                'stat': 'ok',
                'photoset': {
                    'id': '1', 'primary': 'p', 'owner': 'uid2',
                    'photo': [
                        { 'id': '1', 'title': 't' },
                        { 'id': '2', 'title': 't' },
                    ]
                }
            },
            '3': {
                'stat': 'ok',
                'photoset': {
                    'id': '3', 'primary': 'p', 'owner': 'uid2',
                    'photo': [
                        { 'id': '3', 'title': 't' }
                    ]
                }
            }
        }
        flickr = MockFlickrApi()
        getPhotos = lambda **kwargs: json.dumps(
            responses[kwargs['photoset_id']] if kwargs['page'] == 1 \
                    else end_response)
        flickr.photosets.getPhotos = Mock(side_effect=getPhotos)
        file_store = MockFileStore()
        downloader = FlickrApiDownloader(file_store, Mock())
        download_set_photolists(sets, downloader, flickr, 2)
        flickr.photosets.getPhotos.assert_has_calls([
            call(photoset_id='1', page=1, per_page=2, format='json',
                    nojsoncallback=1),
            call(photoset_id='1', page=2, per_page=2, format='json',
                    nojsoncallback=1),
            call(photoset_id='3', page=1, per_page=2, format='json',
                    nojsoncallback=1),
            call(photoset_id='3', page=2, per_page=2, format='json',
                    nojsoncallback=1)
        ])
        file_store.save_json.assert_has_calls([
            call('set-photos/1.json', responses['1']['photoset']['photo']),
            call('set-photos/3.json', responses['3']['photoset']['photo'])
        ])

    def test_paged(self):
        sets = [{'id': '1', 'secret': '2'}]
        pages = [
            {
                'stat': 'ok',
                'photoset': {
                    'id': '1', 'primary': 'p', 'owner': 'uid2',
                    'photo': [
                        { 'id': '1', 'title': 't' },
                        { 'id': '2', 'title': 't' },
                    ]
                },
            },
            {
                'stat': 'ok',
                'photoset': {
                    'id': '1', 'primary': 'p', 'owner': 'uid2',
                    'photo': [
                        { 'id': '3', 'title': 't' },
                    ]
                },
            },
            { 'stat': 'fail', 'code': 1, 'msg': 'Photoset not found' }
        ]
        flickr = MockFlickrApi()
        flickr.photosets.getPhotos = Mock(side_effect=lambda **kwargs: \
                json.dumps(pages[kwargs['page'] - 1]))
        file_store = MockFileStore()
        error_handler = ErrorHandler(StringIO())
        downloader = FlickrApiDownloader(file_store, error_handler)
        download_set_photolists(sets, downloader, flickr, 2)
        flickr.photosets.getPhotos.assert_has_calls([
            call(photoset_id='1', page=1, per_page=2, format='json',
                    nojsoncallback=1),
            call(photoset_id='1', page=2, per_page=2, format='json',
                    nojsoncallback=1),
            call(photoset_id='1', page=3, per_page=2, format='json',
                    nojsoncallback=1)
        ])
        file_store.save_json.assert_called_with('set-photos/1.json', [
            { 'id': '1', 'title': 't' },
            { 'id': '2', 'title': 't' },
            { 'id': '3', 'title': 't' }
        ])
        self.assertFalse(error_handler.has_errors())

    def test_no_such_set(self):
        flickr = MockFlickrApi()
        response = {'stat': 'fail', 'code': 1, 'msg': 'Photoset not found'}
        flickr.photosets.getPhotos = Mock(return_value=json.dumps(response))
        file_store = MockFileStore()
        error_handler = ErrorHandler(StringIO())
        sets = [{'id': '1', 'secret': '2'}]
        downloader = FlickrApiDownloader(file_store, error_handler)
        download_set_photolists(sets, downloader, flickr, 2)
        file_store.save_json.assert_not_called()
        self.assertTrue(error_handler.has_errors())

    @patch('urllib2.AbstractHTTPHandler.do_open')
    def xtest_httpexception(self, mock_do_open):
        import flickr_api
        from flickr_api.api import flickr

        sets = [{'id': '1', 'secret': '2'}]
        error = mock_do_open.side_effect = BadStatusLine('nope')
        flickr_api.set_keys(api_key='test', api_secret='test')
        file_store = Mock()
        error_handler = ErrorHandler(StringIO())
        downloader = FlickrApiDownloader(file_store, error_handler)
        download_set_photolists(sets, downloader, flickr, 2)
        file_store.save_json.assert_not_called()
        params = {'nojsoncallback': 1, 'format': 'json', 'page': 1,
                'per_page': 2, 'photoset_id': '1'}
        self.assertIn((flickr.photosets.getPhotos, params, error),
                error_handler.errors)
