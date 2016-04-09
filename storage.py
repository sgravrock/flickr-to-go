import json
import os
import errno

class FileStore:
    def __init__(self, root_path):
        self.root_path = root_path

    def save_json(self, name, obj):
        filename = self.qualify(name + '.json')
        self.ensure_dir(filename)
        with open(filename, 'w') as f:
            json.dump(obj, f, indent=4)

    def save_image(self, name, data):
        name = self.qualify(name)
        self.ensure_dir(name)
        with open(name, 'wb') as f:
            f.write(data)

    def exists(self, name):
        return os.path.exists(self.qualify(name))

    def credentials_path(self):
        return self.qualify('flickr-credentials')

    def has_saved_credentials(self):
        try:
            with open(self.credentials_path()) as f:
                f.read()
        except IOError:
            return False
        return True

    def ensure_dir(self, filename):
        dirname = os.path.dirname(filename)
        if dirname != '':
            try:
                os.mkdir(dirname)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

    def qualify(self, filename):
        return os.path.join(self.root_path, filename)
