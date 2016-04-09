import requests
import sys

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
