import sys
from urllib2 import HTTPError

def authenticate(flickr_api, auth_handler_class):
  a = auth_handler_class(callback='oob')
  sys.stdout.write("Open this in your browser: %s\n" % a.get_authorization_url('read'))
  sys.stdout.write("Once you finish logging in, enter the code from the browser: \n"),
  code = sys.stdin.readline().strip()

  if code == "":
   return False

  try:
    a.set_verifier(code)
  except HTTPError, e:
    sys.stdout.write("Could not log in. Server returned %s\n" % e.code)
    return False

  flickr_api.set_auth_handler(a)
  return True
