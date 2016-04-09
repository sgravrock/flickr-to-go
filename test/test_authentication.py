import unittest
import sys
import urllib2
from mock import patch
from StringIO import StringIO
from authentication import authenticate

to_raise = None

class MockAuthHandler:
    def __init__(self, callback=None):
        global auth_instance
        self.callback = callback
        self.saved_to = None
        auth_instance = self
    def get_authorization_url(self, perms):
        self.perms = perms
        return 'http://example.com/auth/'
    def set_verifier(self, code):
        global to_raise
        if to_raise:
            raise to_raise
        self.verifier = code
    def save(self, filename):
        self.saved_to = filename

class RejectingMockAuthHandler:
    def __init__(self, callback=None):
        pass
    def get_authorization_url(self, perms):
        raise Exception('Unexpected call to get_authorization_url')

class MockFlickrApi:
    def __init__(self):
        self.test = MockFlickrTestThing()
        self.auth_handler = None
    def set_auth_handler(self, handler):
        self.auth_handler = handler
        self.test.user = {}

class MockFlickrTestThing:
    def login(self):
        return self.user

class MockAuthUi:
    def __init__(self, code, can_error=False):
        self.code = code
        self.can_error = can_error
    def prompt_for_code(self, url):
        self.prompt_url = url
        return self.code
    def error(self, msg):
        if not self.can_error:
            raise Exception('Unexpected error: ' + msg)

class MockCredentialStore:
    def __init__(self, has_saved_creds=False):
        self.has_saved_creds = has_saved_creds
    def credentials_path(self):
        return 'the saved credentials file'
    def has_saved_credentials(self):
        return self.has_saved_creds

class TestAuthentication(unittest.TestCase):
    def setUp(self):
        global to_raise
        to_raise = None

    def test_success(self):
        flickr = MockFlickrApi()
        result = authenticate(False, flickr, MockAuthHandler,
                MockCredentialStore(), MockAuthUi('the code'))
        self.assertIs(result, flickr.test.login())
        self.assertEqual(auth_instance.callback, 'oob')
        self.assertEqual(auth_instance.perms, 'read')
        self.assertEqual(auth_instance.verifier, 'the code')
        self.assertEqual(flickr.auth_handler, auth_instance)

    def test_with_saved_creds(self):
        flickr = MockFlickrApi()
        creds_store = MockCredentialStore(has_saved_creds=True)
        authenticate(False, flickr, RejectingMockAuthHandler, creds_store,
                None)
        self.assertEqual(flickr.auth_handler, 'the saved credentials file')

    def test_EOF(self):
        flickr = MockFlickrApi()
        result = authenticate(False, flickr, MockAuthHandler,
                MockCredentialStore(), MockAuthUi(''))
        self.assertIs(result, None)

    def test_http_error(self):
        global to_raise
        flickr = MockFlickrApi()
        to_raise = urllib2.HTTPError('http://example.com/auth/', 401,
                'nope', None, None)
        result = authenticate(False, flickr, MockAuthHandler,
                MockCredentialStore(), MockAuthUi('c', True))
        self.assertIs(result, None)

    def test_dont_save_creds(self):
        flickr = MockFlickrApi()
        creds_store = MockCredentialStore()
        authenticate(False, flickr, MockAuthHandler, creds_store,
                MockAuthUi('the code'))
        self.assertIs(auth_instance.saved_to, None)

    def test_save_creds(self):
        flickr = MockFlickrApi()
        creds_store = MockCredentialStore()
        authenticate(True, flickr, MockAuthHandler, creds_store,
                MockAuthUi('the code'))
        self.assertEqual(auth_instance.saved_to,
                creds_store.credentials_path())


if __name__ == '__main__':
        unittest.main()

