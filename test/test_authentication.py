import unittest
import sys
import urllib2
from mock import patch, call
from StringIO import StringIO
from authentication import authenticate

AUTH_URL = 'http://example.com/auth/'
AUTO_URL_MSG = 'Please log in using your web browser.'

to_raise = None

class MockAuthHandler:
  def __init__(self, callback=None):
    global auth_instance
    self.callback = callback
    auth_instance = self
  def get_authorization_url(self, perms):
    self.perms = perms
    return AUTH_URL
  def set_verifier(self, code):
    global to_raise
    if to_raise:
      raise to_raise
    self.verifier = code

class MockFlickrApi:
  def set_auth_handler(self, handler):
    self.auth_handler = handler

#class MockSubprocess:
#  def stub_call(args):
#    
#  def call(args, stdin=None, stdout=None, stderr=None, shell=False):
#    pass


@patch('authentication.subprocess')
@patch('sys.stdout', new_callable=StringIO)
class TestAuthentication(unittest.TestCase):
  def setUp(self):
    global to_raise
    to_raise = None

  @patch('sys.stdin', StringIO("the code"))
  def test_success(self, stdout, subprocess):
    flickr = MockFlickrApi()
    subprocess.call.return_value = 0
    result = authenticate(flickr, MockAuthHandler)
    self.assertTrue(result)
    self.assertEqual(subprocess.mock_calls, [call.call(['open', AUTH_URL])])
    # Should not have written the URL, because 'open' worked
    self.assertFalse(AUTH_URL in stdout.getvalue())
    self.assertTrue(AUTO_URL_MSG in stdout.getvalue())
    self.assertEqual(auth_instance.callback, 'oob')
    self.assertEqual(auth_instance.perms, 'read')
    self.assertEqual(auth_instance.verifier, 'the code')
    self.assertEqual(flickr.auth_handler, auth_instance)

#  @patch('sys.stdin', StringIO())
#  def test_EOF(self, stdout, subprocess):
#    flickr = MockFlickrApi()
#    result = authenticate(flickr, MockAuthHandler)
#    self.assertFalse(result)
#
#  @patch('sys.stdin', StringIO("the code"))
#  def test_http_error(self, stdout, subprocess):
#    global to_raise
#    flickr = MockFlickrApi()
#    to_raise = urllib2.HTTPError('http://example.com/auth/', 401, 'nope',
#      None, None)
#    result = authenticate(flickr, MockAuthHandler)
#    self.assertFalse(result)
#
#
if __name__ == '__main__':
    unittest.main()

