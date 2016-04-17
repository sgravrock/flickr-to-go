import json
import os
from httplib import HTTPException

def download(downloader, flickr):
    download_collections(downloader, flickr)
    sets = download_set_list(downloader, flickr)
    download_set_photolists(sets, downloader, flickr)

def download_collections(downloader, flickr):
    return downloader.download(flickr.collections.getTree, {},
            lambda doc: doc['collections'],
            'collections.json')

def download_set_list(downloader, flickr, page_size=500):
    return downloader.paged_download(flickr.photosets.getList, {},
            lambda doc: doc['photosets']['photoset'],
            page_size, 'sets.json')

def download_set_photolists(sets, downloader, flickr, page_size=500):
    for photoset in sets:
        _download_set_photolist(photoset['id'], downloader, flickr, page_size)

def _download_set_photolist(id, downloader, flickr, page_size):
    result = _fetch_set_photolist(id, downloader, flickr, page_size)
    if result:
        filename = os.path.join('set-photos', '%s.json' % id)
        downloader.file_store.save_json(filename, result)

def _fetch_set_photolist(id, downloader, flickr, page_size):
    page_ix = 1
    result = []
    while True:
        # Unlike most paged APIs, photosets.getPhotos returns an error when
        # a nonexistent page is accessed. Unfortunately it also uses the
        # same error code for nonexistent photo sets and malformed params.
        is_past_end = lambda page: \
                page['stat'] == 'fail' and page['code'] == 1 and page_ix != 1
        test_response = lambda page: \
                page['stat'] != 'fail' or is_past_end(page)
        page = downloader.fetch_page(flickr.photosets.getPhotos,
                {'photoset_id': id}, lambda doc: doc,
                page_size, page_ix, test_response)
        if not page:
            return None
        if is_past_end(page):
            return result
        result.extend(page['photoset']['photo'])
        page_ix += 1
