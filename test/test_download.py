import unittest
import json
import urllib2
from httplib import BadStatusLine
import flickr_api
from flickr_api.api import flickr
from mock import Mock, patch
from StringIO import StringIO
from download import FlickrApiDownloader, ErrorHandler

class TestPagedDownload(unittest.TestCase):
    @patch('urllib2.urlopen')
    def test_httpexception(self, mock_urlopen):
        error = mock_urlopen.side_effect = BadStatusLine('nope')
        flickr_api.set_keys(api_key='test', api_secret='test')
        file_store = Mock()
        error_handler = ErrorHandler(StringIO())
        downloader = FlickrApiDownloader(file_store, error_handler)
        result = downloader.paged_download(flickr.people.getPublicPhotos, {},
                lambda doc: doc,
                500, 'ignored')
        self.assertIs(result, None)
        file_store.save_json.assert_not_called()
        params = {'per_page': 500, 'nojsoncallback': 1, 'page': 1,
                'format': 'json'}
        self.assertEqual(error_handler.errors, [
            (flickr.people.getPublicPhotos, params, error)
        ])

    def test_api_error_response(self):
        error_handler = ErrorHandler(StringIO())
        file_store = Mock()
        downloader = FlickrApiDownloader(file_store, error_handler)
        response = {'stat': 'fail', 'code': 1, 'message': 'nope' }
        method = lambda **kwargs: json.dumps(response)
        result = downloader.paged_download(method, {}, lambda doc: doc,
                500, 'ignored')
        self.assertIs(result, None)
        file_store.save_json.assert_not_called()
        params = {'per_page': 500, 'nojsoncallback': 1, 'page': 1,
                'format': 'json'}
        self.assertEqual(error_handler.errors, [(method, params, response)])

class TestDownload(unittest.TestCase):
    @patch('urllib2.urlopen')
    def test_httpexception(self, mock_urlopen):
        error = mock_urlopen.side_effect = BadStatusLine('nope')
        flickr_api.set_keys(api_key='test', api_secret='test')
        file_store = Mock()
        error_handler = ErrorHandler(StringIO())
        downloader = FlickrApiDownloader(file_store, error_handler)
        result = downloader.download(flickr.people.getPublicPhotos, {},
                lambda doc: doc,
                'ignored')
        self.assertIs(result, None)
        file_store.save_json.assert_not_called()
        params = {'nojsoncallback': 1, 'format': 'json'}
        self.assertEqual(error_handler.errors, [
            (flickr.people.getPublicPhotos, params, error)
        ])

    def test_api_error_response(self):
        file_store = Mock()
        error_handler = ErrorHandler(StringIO())
        downloader = FlickrApiDownloader(file_store, error_handler)
        response = {'stat': 'fail', 'code': 1, 'message': 'nope' }
        method = lambda **kwargs: json.dumps(response)
        result = downloader.download(method, {}, lambda doc: doc,
                'ignored')
        self.assertIs(result, None)
        file_store.save_json.assert_not_called()
        params = {'nojsoncallback': 1, 'format': 'json'}
        self.assertEqual(error_handler.errors, [(method, params, response)])
