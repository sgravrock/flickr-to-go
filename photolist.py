import json
import re

def download(downloader, flickrApiClient, page_size=500):
    return downloader.paged_download(flickrApiClient, 'people.getPhotos',
            {'user_id': 'me', 'extras': 'url_o'},
            lambda doc: doc['photos']['photo'],
            page_size, 'photos.json')

def fetch_recently_updated(timestamp, downloader, flickrApiClient, page_size=500):
    return downloader.paged_fetch(flickrApiClient, 'photos.recentlyUpdated',
            {'min_date': timestamp},
            lambda doc: [p['id'] for p in doc['photos']['photo']],
            page_size)
