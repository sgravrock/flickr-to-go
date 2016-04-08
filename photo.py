import requests

def download_originals(photolist, file_store, requests=requests):
    for photo in photolist:
        print("Downloading %s" % photo['id'])
        response = requests.get(photo['url_o'])
        file_store.save_image(original_filename(photo), response.content)

def original_filename(photo):
    return 'originals/%s_o.jpg' % photo['id']
