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
    auth_instance = self
  def get_authorization_url(self, perms):
    self.perms = perms
    return 'http://example.com/auth/'
  def set_verifier(self, code):
    global to_raise
    if to_raise:
      raise to_raise
    self.verifier = code

class MockFlickrApi:
  def set_auth_handler(self, handler):
    self.auth_handler = handler
    
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

class TestAuthentication(unittest.TestCase):
  def setUp(self):
    global to_raise
    to_raise = None

  def test_success(self):
    flickr = MockFlickrApi()
    result = authenticate(flickr, MockAuthHandler, MockAuthUi('the code'))
    self.assertTrue(result)
    self.assertEqual(auth_instance.callback, 'oob')
    self.assertEqual(auth_instance.perms, 'read')
    self.assertEqual(auth_instance.verifier, 'the code')
    self.assertEqual(flickr.auth_handler, auth_instance)

  def test_EOF(self):
    flickr = MockFlickrApi()
    result = authenticate(flickr, MockAuthHandler, MockAuthUi(''))
    self.assertFalse(result)

  def test_http_error(self):
    global to_raise
    flickr = MockFlickrApi()
    to_raise = urllib2.HTTPError('http://example.com/auth/', 401, 'nope',
      None, None)
    result = authenticate(flickr, MockAuthHandler, MockAuthUi('c', True))
    self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

