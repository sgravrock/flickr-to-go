import json

def paged_download(file_store, method, extra_params, data_accessor, page_size,
        dest_path):
    result = fetch(method, extra_params, data_accessor, page_size)
    file_store.save_json(dest_path, result)
    return result

def fetch(method, extra_params, data_accessor, page_size):
    page_ix = 1
    result = []
    while True:
        page = fetch_page(method, extra_params, data_accessor,
                page_size, page_ix)
        result.extend(page)
        if len(page) < page_size:
            return result
        page_ix += 1

def fetch_page(method, extra_params, data_accessor, page_size, page_ix):
    params = {'page': page_ix, 'per_page': page_size, 'format': 'json',
            'nojsoncallback': 1}
    params.update(extra_params)
    doc = method(**params)
    return data_accessor(json.loads(doc))

