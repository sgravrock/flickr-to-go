import sys
import subprocess
from requests_oauthlib import OAuth1Session
from requests_oauthlib.oauth1_session import TokenRequestDenied


request_token_url = 'https://www.flickr.com/services/oauth/request_token'
base_authorization_url = 'https://www.flickr.com/services/oauth/authorize'
access_token_url = 'https://www.flickr.com/services/oauth/access_token'

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

def authenticate(savecreds, api_key, api_secret, credential_store, 
        ui_adapter=None):
    access_token = credential_store.saved_credentials()
    if access_token:
        return create_session(api_key, api_secret, access_token)
    else:
        return authenticate_interactive(savecreds, api_key, api_secret,
                credential_store, ui_adapter)

def create_session(api_key, api_secret, access_token):
    return OAuth1Session(api_key,
                         client_secret=api_secret,
                         resource_owner_key=access_token['token'],
                         resource_owner_secret=access_token['secret'])

def authenticate_interactive(savecreds, api_key, api_secret,
        credential_store, ui_adapter):
    if not ui_adapter:
        ui_adapter = AuthConsoleUi()

    session = OAuth1Session(api_key, client_secret=api_secret, callback_uri='oob')
    request_token = get_request_token(session)
    authz_url = session.authorization_url(base_authorization_url, perms='read')
    verifier = ui_adapter.prompt_for_code(authz_url)
    if verifier == "":
        return False
    
    try:
        access_token = get_access_token(api_key, api_secret, request_token, verifier)
    except TokenRequestDenied:
        ui_adapter.error('Login failed.')
        return False

    if savecreds:
        credential_store.save_credentials(access_token)

    return create_session(api_key, api_secret, access_token)

def get_request_token(session):
    response = session.fetch_request_token(request_token_url)
    return {
        'token': response.get('oauth_token'),
        'secret': response.get('oauth_token_secret')
    }

def get_access_token(api_key, api_secret, request_token, verifier):
    session = OAuth1Session(api_key,
                            client_secret=api_secret,
                            resource_owner_key=request_token['token'],
                            resource_owner_secret=request_token['secret'],
                            verifier=verifier)
    response = session.fetch_access_token(access_token_url)
    return {
        'token': response.get('oauth_token'),
        'secret': response.get('oauth_token_secret')
    }
