import os
import sys
import time
import flickr_api
from flickr_api import auth
from flickr_api.api import flickr
from authentication import authenticate
from storage import FileStore
import photolist
import photo
import containers
import download
from download import FlickrApiDownloader, ErrorHandler


def flickr_to_go(dest, savecreds, key, secret, output=sys.stdout):
    start_time = time.time()
    timestamp_path = os.path.join(dest, 'timestamp')
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
        if photos is None:
            output.write("Photo list download failed. Can't continue.\n")
            return False
        containers.download(downloader, flickr)
        last_time = read_timestamp(timestamp_path)
        if last_time is None:
            recently_updated = []
        else:
            recently_updated = photolist.fetch_recently_updated(last_time,
                downloader, flickr) or []
        photo.download(photos, recently_updated, downloader, flickr)

        if errors.has_errors():
            print("Some requests failed.")
            print("Errors are logged to %s" % err_path)
            return False

    with open(timestamp_path, 'w') as f:
        f.write(str(int(round(start_time))))
    return True

def read_timestamp(path):
    try:
        with open(path) as f:
            return int(f.read())
    except IOError:
        return None
