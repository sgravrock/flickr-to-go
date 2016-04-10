import json
import re

def download(downloader, flickr, page_size=500):
    return downloader.paged_download(flickr.people.getPhotos,
            {'user_id': 'me', 'extras': 'url_o'},
            lambda doc: doc['photos']['photo'],
            page_size, 'photos.json')
