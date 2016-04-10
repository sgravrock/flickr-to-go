import requests
import sys
import os
import json
from paged_download import download

def download_originals(photolist, file_store, requests=requests,
        logger=sys.stdout):
    for photo in photolist:
        filename = original_filename(photo)
        if not file_store.exists(filename):
            logger.write("Downloading %s\n" % photo['id'])
            response = requests.get(photo['url_o'])
            file_store.save_image(filename, response.content)

def original_filename(photo):
    return 'originals/%s_o.jpg' % photo['id']

def download_info(photolist, file_store, flickr, error_handler,
        logger=sys.stdout):
    for photo in photolist:
        filename = info_filename(photo)
        if not file_store.exists(filename):
            logger.write("Downloading info for %s\n" % photo['id'])
            download(file_store, error_handler, flickr.photos.getInfo,
                    {'photo_id': photo['id']},
                    lambda doc: doc['photo'], filename)

def info_filename(photo):
    return os.path.join('photo-info', '%s.json' % photo['id'])
