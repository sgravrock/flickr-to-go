import os
import sys
import flickr_api
from flickr_api import auth

a = auth.AuthHandler(key=os.environ['FLICKR_API_KEY'], secret=os.environ['FLICKR_API_SECRET'], callback='oob')
print("Open this in your browser: " + a.get_authorization_url('read'))
print("Once you finish logging in, enter the code from the browser: "),
code = sys.stdin.readline().strip()

a.set_verifier(code)
flickr_api.set_auth_handler(a)
user = flickr_api.test.login()

photos = user.getPhotos()
print "Got %s photos" % photos.info.total
