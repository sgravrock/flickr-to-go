import json

def download_collections(file_store, flickr):
    raw = flickr.collections.getTree(format='json', nojsoncallback=1)
    result = json.loads(raw)['collections']
    file_store.save_json('collections.json', result)
    return result

def download_set_list(file_store, flickr, page_size=500):
    result = fetch_set_list(flickr, page_size)
    file_store.save_json('sets.json', result)
    return result

def fetch_set_list(flickr, page_size):
    page_ix = 1
    result = []
    while True:
        page = fetch_set_list_page(flickr, page_size, page_ix)
        result.extend(page)
        if len(page) < page_size:
            return result
        page_ix += 1

def fetch_set_list_page(flickr, page_size, page_ix):
    doc = flickr.photosets.getList(page=page_ix, per_page=page_size,
            format='json', nojsoncallback=1)
    return json.loads(doc)['photosets']['photoset']
