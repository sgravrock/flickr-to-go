import json
import re

def download(downloader, flickr, page_size=500):
    return downloader.paged_download(flickr.people.getPhotos,
            {'user_id': 'me', 'extras': 'url_o'},
            lambda doc: doc['photos']['photo'],
            page_size, 'photos.json')

def fetch_recently_updated(timestamp, downloader, flickr, page_size=500):
    return downloader.paged_fetch(flickr.photos.recentlyUpdated,
            {'min_date': timestamp},
            lambda doc: [p['id'] for p in doc['photos']['photo']],
            page_size)
