import os
import flickr_api
from flickr_api import auth
from flickr_api.api import flickr
from authentication import authenticate
from storage import FileStore
import photolist
import photo
import containers
from download import FlickrApiDownloader, ErrorHandler

def flickr_to_go(dest, savecreds, key, secret):
    flickr_api.set_keys(api_key=key, api_secret=secret)
    file_store = FileStore(dest)
    user = authenticate(savecreds, flickr_api, auth.AuthHandler, file_store)
    if not user:
        return False

    err_path = os.path.join(dest, "errors.txt")
    with open(err_path, 'w') as errfile:
        errors = ErrorHandler(errfile)
        downloader = FlickrApiDownloader(file_store, errors)
        photos = photolist.download(downloader, flickr)
        containers.download(downloader, flickr)
        photo.download(photos, downloader, flickr)

        if errors.has_errors():
            print("Some requests failed.")
            print("Errors are logged to %s" % err_path)
            return False

    return True
