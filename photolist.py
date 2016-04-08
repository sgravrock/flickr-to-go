import json
import re

def download(file_store, flickr, page_size=500):
    photos = fetch(flickr, page_size)
    file_store.save_json('photos', photos)
    return photos

def fetch(flickr, page_size):
    page_ix = 1
    result = []
    while True:
        page = fetch_page(flickr, page_size, page_ix)
        result.extend(page)
        if len(page) < page_size:
            return result
        page_ix += 1

def fetch_page(flickr, page_size, page_ix):
    doc = flickr.people.getPhotos(user_id='me', page=page_ix,
            per_page=page_size, format='json', nojsoncallback=1,
            extras='url_o')
    return json.loads(doc)['photos']['photo']
