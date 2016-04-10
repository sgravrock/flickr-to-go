import unittest
import json
import urllib2
from httplib import BadStatusLine
import flickr_api
from flickr_api.api import flickr
from mock import Mock, patch
from StringIO import StringIO
from download import download, paged_download, ErrorHandler

class TestPagedDownload(unittest.TestCase):
    @patch('urllib2.AbstractHTTPHandler.do_open')
    def test_httpexception(self, mock_do_open):
        error = mock_do_open.side_effect = BadStatusLine('nope')
        flickr_api.set_keys(api_key='test', api_secret='test')
        file_store = Mock()
        error_handler = ErrorHandler(StringIO())
        result = paged_download(file_store, error_handler,
                flickr.people.getPublicPhotos, {},
                lambda doc: doc,
                500, 'ignored')
        self.assertIs(result, None)
        file_store.save_json.assert_not_called()
        params = {'per_page': 500, 'nojsoncallback': 1, 'page': 1,
                'format': 'json'}
        self.assertEqual(error_handler.errors, [
            (flickr.people.getPublicPhotos, params, error)
        ])

class TestDownload(unittest.TestCase):
    @patch('urllib2.AbstractHTTPHandler.do_open')
    def test_httpexception(self, mock_do_open):
        error = mock_do_open.side_effect = BadStatusLine('nope')
        flickr_api.set_keys(api_key='test', api_secret='test')
        file_store = Mock()
        error_handler = ErrorHandler(StringIO())
        result = download(file_store, error_handler,
                flickr.people.getPublicPhotos, {},
                lambda doc: doc,
                'ignored')
        self.assertIs(result, None)
        file_store.save_json.assert_not_called()
        params = {'nojsoncallback': 1, 'format': 'json'}
        self.assertEqual(error_handler.errors, [
            (flickr.people.getPublicPhotos, params, error)
        ])
