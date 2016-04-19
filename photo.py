import requests
import sys
import os
import json

def download(photos, downloader, flickr):
    download_originals(photos, downloader.file_store)
    download_info(photos, downloader, flickr)

def download_originals(photolist, file_store, requests=requests,
        logger=sys.stdout):
    for photo in photolist:
        _download_original(photo, file_store, requests, logger)

def _download_original(photo, file_store, requests, logger):
    filename = original_filename(photo)
    if not file_store.exists(filename):
        logger.write("Downloading %s\n" % photo['id'])
        for i in xrange(0, 3):
            try:
                response = requests.get(photo['url_o'])
            except Exception, e:
                if i == 2:
                    raise
        file_store.save_image(filename, response.content)
        return

def original_filename(photo):
    return 'originals/%s_o.jpg' % photo['id']

def download_info(photolist, downloader, flickr, logger=sys.stdout):
    for photo in photolist:
        filename = info_filename(photo)
        if not downloader.file_store.exists(filename):
            logger.write("Downloading info for %s\n" % photo['id'])
            downloader.download(flickr.photos.getInfo,
                    {'photo_id': photo['id']},
                    lambda doc: doc['photo'], filename)

def info_filename(photo):
    return os.path.join('photo-info', '%s.json' % photo['id'])
