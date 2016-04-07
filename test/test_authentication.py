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
    

@patch('sys.stdout', new_callable=StringIO)
class TestAuthentication(unittest.TestCase):
  def setUp(self):
    global to_raise
    to_raise = None

  @patch('sys.stdin', StringIO("the code"))
  def test_success(self, stdout):
    flickr = MockFlickrApi()
    result = authenticate(flickr, MockAuthHandler)
    self.assertTrue(result)
    self.assertEqual(auth_instance.callback, 'oob')
    self.assertEqual(auth_instance.perms, 'read')
    self.assertEqual(auth_instance.verifier, 'the code')
    self.assertEqual(flickr.auth_handler, auth_instance)

  @patch('sys.stdin', StringIO())
  def test_EOF(self, stdout):
    flickr = MockFlickrApi()
    result = authenticate(flickr, MockAuthHandler)
    self.assertFalse(result)

  @patch('sys.stdin', StringIO("the code"))
  def test_http_error(self, stdout):
    global to_raise
    flickr = MockFlickrApi()
    to_raise = urllib2.HTTPError('http://example.com/auth/', 401, 'nope',
      None, None)
    result = authenticate(flickr, MockAuthHandler)
    self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

