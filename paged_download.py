import json
from httplib import HTTPException
import sys
import traceback

def paged_download(file_store, error_handler, method, extra_params,
        data_accessor, page_size, dest_path):
    result = _paged_fetch(error_handler, method, extra_params, data_accessor,
            page_size)
    if result:
        file_store.save_json(dest_path, result)
    return result

def _paged_fetch(error_handler, method, extra_params, data_accessor, page_size):
    page_ix = 1
    result = []
    while True:
        page = fetch_page(error_handler, method, extra_params, data_accessor,
                page_size, page_ix)
        if page is None:
            return None
        result.extend(page)
        if len(page) < page_size:
            return result
        page_ix += 1

def fetch_page(error_handler, method, extra_params, data_accessor, page_size,
        page_ix):
    params = _combine(extra_params, {'page': page_ix, 'per_page': page_size,
            'format': 'json', 'nojsoncallback': 1})
    try:
        doc = method(**params)
    except HTTPException, e:
        error_handler.add_error(method, params, e)
        return None
    return data_accessor(json.loads(doc))


def download(file_store, error_handler, method, params, data_accessor,
        dest_path):
    params = _combine(params, {'format': 'json', 'nojsoncallback': 1})
    try:
        doc = method(**params)
    except HTTPException, e:
        error_handler.add_error(method, params, e)
        return None
    result = data_accessor(json.loads(doc))
    file_store.save_json(dest_path, result)
    return result


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
