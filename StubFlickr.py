import json

class StubFlickrBuilder:
    def photolist(self, photos):
        self._photolist = [photolist_entry(p) for p in photos]
        return self
    def build(self):
        return StubFlickrApi(self._photolist)


class StubFlickrApi:
    def __init__(self, photolist):
        self.people = StubFlickrPeople(photolist)
        self.collections = StubFlickrCollections()
        self.photosets = StubFlickrPhotosets()
        self.photos = StubFlickrPhotos()

class StubFlickrPeople:
    def __init__(self, photolist):
        self._photolist = photolist
    def getPhotos(self, **kwargs):
        return json.dumps({'photos': {'photo': self._photolist}})

class StubFlickrPhotos:
    def getInfo(self, **kwargs):
        return json.dumps({'photo': {}})

class StubFlickrCollections:
    def getTree(self, **kwargs):
        return json.dumps({'collections': {}})

class StubFlickrPhotosets:
    def getList(self, **kwargs):
        # TODO: Fix the system to cope with an empty list of sets,
        # then remove the defaults here.
        return json.dumps({
            'stat': 'ok',
            'photosets': {
                'photoset': [
                    { 'id': 1, 'secret': '2' }
                ]
            }
        })
    def getPhotos(self, **kwargs):
        if kwargs['page'] == 1:
            return json.dumps({
                'stat': 'ok',
                'photoset': {
                    'photo': []
                }
            })
        else:
            return json.dumps({
                'stat': 'fail',
                'code': 1
            })

def photolist_entry(photo):
    if 'id' not in photo:
        raise Exception('Each photo requires at least an ID')
    result = {'owner': '21041082@N02','secret': 'x',
        'server': '1521','farm': 2,'title': '','ispublic': 1,
        'isfriend': 0, 'isfamily': 0}
    for k in photo:
        result[k] = photo[k]
    return result

