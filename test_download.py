import unittest
import json
import urllib2
from httplib import BadStatusLine
# import flickr_api
# from flickr_api.api import flickr
from mock import Mock, patch
from StringIO import StringIO
from download import FlickrApiDownloader, ErrorHandler

class FailsTwice:
    def __init__(self, successful_response):
        self.successful_response = successful_response
        self.count = 0

    def urlopen(self, url):
        self.count += 1
        if self.count == 3:
            return self.successful_response
        else:
            raise BadStatusLine('nope')

class TestPagedDownload(unittest.TestCase):
    @patch('urllib2.urlopen')
    def xtest_httpexception(self, mock_urlopen):
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
        self.assertIn((flickr.people.getPublicPhotos, params, error),
                error_handler.errors)

    def xtest_api_error_response(self):
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
        self.assertIn((method, params, response), error_handler.errors)

class TestDownload(unittest.TestCase):
    @patch('urllib2.urlopen')
    def xtest_httpexception_fails(self, mock_urlopen):
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
        self.assertIn((flickr.people.getPublicPhotos, params, error),
                error_handler.errors)

    @patch('urllib2.urlopen')
    def xtest_httpexception_retry_success(self, mock_urlopen):
        handler = FailsTwice(StringIO('{"x": 42}'))
        mock_urlopen.side_effect = lambda *args: handler.urlopen(args[0])
        flickr_api.set_keys(api_key='test', api_secret='test')
        error_handler = ErrorHandler(StringIO())
        downloader = FlickrApiDownloader(Mock(), error_handler)
        result = downloader.download(flickr.people.getPublicPhotos, {},
                lambda doc: doc,
                'ignored')
        self.assertEqual(result, {'x': 42})

    def xtest_api_error_response_fails(self):
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
        self.assertIn((method, params, response), error_handler.errors)

    def xtest_api_error_response_retry_success(self):
        file_store = Mock()
        error_handler = ErrorHandler(StringIO())
        downloader = FlickrApiDownloader(file_store, error_handler)
        error = {'stat': 'fail', 'code': 1, 'message': 'nope' }
        success_response = {'x': 42}
        responses = [json.dumps(x) for x in (error, error, success_response)]
        method = Mock(side_effect=responses)
        result = downloader.download(method, {}, lambda doc: doc,
                'ignored')
        self.assertEqual(result, success_response)
        params = {'nojsoncallback': 1, 'format': 'json'}
        self.assertIn((method, params, error), error_handler.errors)
