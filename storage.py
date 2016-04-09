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

    def exists(self, name):
        return os.path.exists(name)

    def credentials_path(self):
        return 'flickr-credentials'

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
