import requests

def download_originals(photolist, file_store, requests=requests):
    for photo in photolist:
        filename = original_filename(photo)
        if not file_store.exists(filename):
            print("Downloading %s" % photo['id'])
            response = requests.get(photo['url_o'])
            file_store.save_image(filename, response.content)

def original_filename(photo):
    return 'originals/%s_o.jpg' % photo['id']
