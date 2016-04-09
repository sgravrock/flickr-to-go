import sys
import subprocess
from urllib2 import HTTPError

class AuthConsoleUi:
    def __init__(self, stdin=sys.stdin, stdout=sys.stdout,
                 stderr=sys.stderr, subprocess=subprocess):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.subprocess = subprocess

    def prompt_for_code(self, url):
        if self.subprocess.call(['open', url]) == 0:
            self.stdout.write('The Flickr login page should have opened ' +
                    'in your browser. Please log in.\n')
        else:
            self.stdout.write("Open this in your browser: %s\n" % url)
        self.stdout.write("After you've finished logging in, enter the " +
                "code from your browser: \n"),
        return self.stdin.readline().strip()

    def error(self, msg):
        self.stderr.write(msg + "\n")


def authenticate(savecreds, flickr_api, auth_handler_class,
        credential_store, ui_adapter=None):
    if credential_store.has_saved_credentials():
        ok = authenticate_saved(flickr_api, credential_store)
    else:
        ok = authenticate_interactive(savecreds, flickr_api,
                auth_handler_class, credential_store, ui_adapter)
    if ok:
        return flickr_api.test.login()

def authenticate_saved(flickr_api, credential_store):
    flickr_api.set_auth_handler(credential_store.credentials_path())
    # TODO: Can this fail? If so, how do we detect it?
    return True

def authenticate_interactive(savecreds, flickr_api, auth_handler_class,
        credential_store, ui_adapter):
    if not ui_adapter:
        ui_adapter = AuthConsoleUi()

    a = auth_handler_class(callback='oob')
    code = ui_adapter.prompt_for_code(a.get_authorization_url('read'))
    if code == "":
        return False

    try:
        a.set_verifier(code)
    except HTTPError, e:
        ui_adapter.error("Could not log in. Server returned %s." % e.code)
        return False
    flickr_api.set_auth_handler(a)
    if savecreds:
        a.save(credential_store.credentials_path())
    return True
