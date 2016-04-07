import unittest
import sys
import urllib2
from authentication import authenticate

to_raise = None

class MockReadable:
  def __init__(self, contents):
    self.contents = contents
  def readline(self):
    if len(self.contents) == 0:
      return '' # EOF
    return self.contents.pop(0)

class MockWriteable:
  def write(self, s):
    pass

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
    

class TestAuthentication(unittest.TestCase):
  def setUp(self):
    global to_raise
    to_raise = None
  def test_success(self):
    input = MockReadable(['the code'])
    output = MockWriteable()
    flickr = MockFlickrApi()
    result = authenticate(flickr, MockAuthHandler, output, input)
    self.assertTrue(result)
    self.assertEqual(auth_instance.callback, 'oob')
    self.assertEqual(auth_instance.perms, 'read')
    self.assertEqual(auth_instance.verifier, 'the code')
    self.assertEqual(flickr.auth_handler, auth_instance)

  def test_EOF(self):
    input = MockReadable([])
    output = MockWriteable()
    flickr = MockFlickrApi()
    result = authenticate(flickr, MockAuthHandler, output, input)
    self.assertFalse(result)

  def test_http_error(self):
    global to_raise
    input = MockReadable(['the code'])
    output = MockWriteable()
    flickr = MockFlickrApi()
    to_raise = urllib2.HTTPError('http://example.com/auth/', 401, 'nope',
      None, None)
    result = authenticate(flickr, MockAuthHandler, output, input)
    self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

