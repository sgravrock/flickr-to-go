import json
import os
from download import download, paged_download, fetch_page
from httplib import HTTPException


def download_collections(file_store, error_handler, flickr):
    return download(file_store, error_handler, flickr.collections.getTree, {},
            lambda doc: doc['collections'],
            'collections.json')

def download_set_list(file_store, error_handler, flickr, page_size=500):
    return paged_download(file_store, error_handler, flickr.photosets.getList,
            {},
            lambda doc: doc['photosets']['photoset'],
            page_size, 'sets.json')

def download_set_photolists(sets, file_store, flickr, error_handler,
        page_size=500):
    for photoset in sets:
        _download_set_photolist(photoset['id'], file_store, flickr,
                error_handler, page_size)

def _download_set_photolist(id, file_store, flickr, error_handler, page_size):
    result = _fetch_set_photolist(id, flickr, error_handler, page_size)
    if result:
        filename = os.path.join('set-photos', '%s.json' % id)
        file_store.save_json(filename, result)

def _fetch_set_photolist(id, flickr, error_handler, page_size):
    page_ix = 1
    result = []
    while True:
        page = fetch_page(error_handler, flickr.photosets.getPhotos,
                {'photoset_id': id}, lambda doc: doc,
                page_size, page_ix)
        if not page:
            return None
        # Unlike most paged APIs, photosets.getPhotos returns an error when
        # a nonexistent page is accessed. Unfortunately it also uses the
        # same error code for nonexistent photo sets and malformed params.
        if page['stat'] == 'fail':
            if page['code'] == 1:
                return result
            else:
                return None # TODO: report?

        result.extend(page['photoset']['photo'])
        page_ix += 1
