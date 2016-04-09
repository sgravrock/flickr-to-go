import json
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
