import os
import sys
import time
# TODO: combine authentication and flickr_api_client?
from authentication import authenticate
from flickr_api_client import FlickrApiClient
from storage import FileStore
import photolist
import photo
import containers
import download
from download import FlickrApiDownloader, ErrorHandler


def flickr_to_go(dest, savecreds, key, secret, output=sys.stdout):
    start_time = time.time()
    timestamp_path = os.path.join(dest, 'timestamp')
    file_store = FileStore(dest)
    session = authenticate(savecreds, key, secret, file_store)
    if not session:
        return False

    client = FlickrApiClient(session)
    err_path = os.path.join(dest, "errors.txt")
    with open(err_path, 'w') as errfile:
        errors = ErrorHandler(errfile)
        downloader = FlickrApiDownloader(file_store, errors)
        photos = photolist.download(downloader, client)
        if photos is None:
            output.write("Photo list download failed. Can't continue.\n")
            return False
        # containers.download(downloader, flickr)
        # last_time = read_timestamp(timestamp_path)
        # if last_time is None:
        #     recently_updated = []
        # else:
        #     recently_updated = photolist.fetch_recently_updated(last_time,
        #         downloader, flickr) or []
        # photo.download(photos, recently_updated, downloader, flickr)

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
