import os
import flickr_api
from flickr_api import auth
from flickr_api.api import flickr
from authentication import authenticate
from storage import FileStore
import photolist
import photo
import containers
from paged_download import ErrorHandler

def flickr_to_go(dest, savecreds, key, secret):
    flickr_api.set_keys(api_key=key, api_secret=secret)
    file_store = FileStore(dest)
    user = authenticate(savecreds, flickr_api, auth.AuthHandler, file_store)
    if not user:
        return False

    err_path = os.path.join(dest, "errors.txt")
    with open(err_path, 'w') as errfile:
	    errors = ErrorHandler(errfile)
	    photos = photolist.download(file_store, errors, flickr)
	    containers.download_collections(file_store, errors, flickr)
	    sets = containers.download_set_list(file_store, errors, flickr)
	    containers.download_set_photolists(sets, file_store, flickr, errors)
	    photo.download_originals(photos, file_store)
	    photo.download_info(photos, file_store, flickr, errors)

	    if errors.has_errors():
	        print("Some requests failed.")
	        print("Errors are logged to %s" % err_path)
            return False

    return True
