import json

def download_collections(file_store, flickr):
    raw = flickr.collections.getTree(format='json', nojsoncallback=1)
    result = json.loads(raw)['collections']
    file_store.save_json('collections.json', result)
    return result
