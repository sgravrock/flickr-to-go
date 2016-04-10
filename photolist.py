import json
import re
from paged_download import paged_download

def download(file_store, error_handler, flickr, page_size=500):
    return paged_download(file_store, error_handler, flickr.people.getPhotos,
            {'user_id': 'me', 'extras': 'url_o'},
            lambda doc: doc['photos']['photo'],
            page_size, 'photos.json')
