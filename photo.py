import requests
import sys
import os
import json

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

def download_info(photolist, file_store, flickr, logger=sys.stdout):
    for photo in photolist:
        logger.write("Downloading info for %s\n" % photo['id'])
        raw = flickr.photos.getInfo(photo_id=photo['id'], format='json',
               nojsoncallback=1)
        info = json.loads(raw)['photo']
        file_store.save_json(os.path.join('photo-info', photo['id']), info)

