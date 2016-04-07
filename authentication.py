import sys
from urllib2 import HTTPError

def authenticate(flickr_api, auth_handler_class, out=sys.stdout, input=sys.stdin):
  a = auth_handler_class(callback='oob')
  out.write("Open this in your browser: %s\n" % a.get_authorization_url('read'))
  out.write("Once you finish logging in, enter the code from the browser: \n"),
  code = input.readline().strip()

  if code == "":
   return False

  try:
    a.set_verifier(code)
  except HTTPError, e:
    out.write("Could not log in. Server returned %s\n" % e.code)
    return False

  flickr_api.set_auth_handler(a)
  return True
