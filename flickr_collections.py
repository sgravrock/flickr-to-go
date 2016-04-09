import json

def download(file_store, flickr):
    raw = flickr.collections.getTree(format='json', nojsoncallback=1)
    result = json.loads(raw)['collections']
    file_store.save_json('collections', result)
    return result
