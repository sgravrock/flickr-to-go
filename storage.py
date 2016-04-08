import json
import os
import errno

class FileStore:
    def save_json(self, name, obj):
        with open(name + '.json', 'w') as f:
            json.dump(obj, f, indent=4)

    def save_image(self, name, data):
        self.ensure_dir(name)
        with open(name, 'wb') as f:
            f.write(data)

    def ensure_dir(self, filename):
        dirname = os.path.dirname(filename)
        if dirname != '':
            try:
                os.mkdir(dirname)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
