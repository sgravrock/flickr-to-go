import json
from httplib import HTTPException
import sys
import traceback

def _standard_test_response(response):
    return response.get('stat') != 'fail'

class FlickrApiDownloader:
    def __init__(self, file_store, error_handler):
        self.file_store = file_store
        self.error_handler = error_handler

    def download(self, method, params, data_accessor, dest_path):
        # TODO: do this in the client itself
        # params = _combine(params, {'format': 'json', 'nojsoncallback': 1})
        result = self._fetch(method, params, data_accessor,
                _standard_test_response)
        if result:
            self.file_store.save_json(dest_path, result)
        return result

    def paged_download(self, client, method, params, data_accessor, page_size,
            dest_path):
        result = self.paged_fetch(client, method, params, data_accessor, page_size)
        if result:
            self.file_store.save_json(dest_path, result)
        return result

    def fetch_page(self, client, method, extra_params, data_accessor, page_size,
            page_ix, test_response=_standard_test_response):
        # TODO: add format and nojsoncallback in the client itself
        params = _combine(extra_params, {'page': page_ix, 
            'per_page': page_size})
        return self._fetch(client, method, params, data_accessor, test_response)

    def paged_fetch(self, client, method, extra_params, data_accessor, page_size):
        page_ix = 1
        result = []
        while True:
            page = self.fetch_page(client, method, extra_params, data_accessor,
                    page_size, page_ix)
            if page is None:
                return None
            result.extend(page)
            if len(page) < page_size:
                return result
            page_ix += 1

    def _fetch(self, client, method, params, data_accessor, test_response):
        for i in xrange(0, 3):
            result = self._fetch_once(client, method, params, data_accessor,
                    test_response)
            if result:
                return result

    def _fetch_once(self, client, method, params, data_accessor, test_response):
        # try:
        doc = client.get(method, params)
        # except HTTPException, e:
            # self.error_handler.add_error(method, params, e)
            # return None
        if not test_response(doc):
            self.error_handler.add_error(method, params, doc)
            return None
        return data_accessor(doc)



class ErrorHandler:
    def __init__(self, file):
        self.errors = []
        self._file = file

    def add_error(self, method, params, error):
        self.errors.append((method, params, error))
        self._file.write("Error calling %s with params:\n%s\n%s\n" %
                (method, params, self._format_traceback(error)))

    def has_errors(self):
        return len(self.errors) > 0

    def _format_traceback(self, ex):
        _, _, ex_traceback = sys.exc_info()
        lines = traceback.format_exception(ex.__class__, ex, ex_traceback)
        return ''.join(lines)



def _combine(dict1, dict2):
    result = dict1.copy()
    result.update(dict2)
    return result
