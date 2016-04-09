import json
import os
from paged_download import paged_download

def download_collections(file_store, flickr):
    raw = flickr.collections.getTree(format='json', nojsoncallback=1)
    result = json.loads(raw)['collections']
    file_store.save_json('collections.json', result)
    return result

def download_set_list(file_store, flickr, page_size=500):
    return paged_download(file_store, flickr.photosets.getList, {},
            lambda doc: doc['photosets']['photoset'],
            page_size, 'sets.json')

def download_set_photolists(sets, file_store, flickr, page_size=500):
    for photoset in sets:
        _download_set_photolist(photoset['id'], file_store, flickr, page_size)

def _download_set_photolist(id, file_store, flickr, page_size):
    result = _fetch_set_photolist(id, flickr, page_size)
    filename = os.path.join('set-photos', '%s.json' % id)
    file_store.save_json(filename, result)

def _fetch_set_photolist(id, flickr, page_size):
    page_ix = 1
    result = []
    while True:
        raw = flickr.photosets.getPhotos(format='json', nojsoncallback=1,
             photoset_id=id, page=page_ix, per_page=page_size)
        page = json.loads(raw)
        # Unlike most paged APIs, photosets.getPhotos returns an error when
        # a nonexistent page is accessed. Unfortunately it also uses the
        # same error code for nonexistent photo sets and malformed params.
        if page['stat'] == 'fail':
            if page['code'] == 1:
                return result
            else:
                return None # TODO: raise instead?

        result.extend(page['photoset']['photo'])
        page_ix += 1
