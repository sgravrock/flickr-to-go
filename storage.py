import json

class FileStore:
    def save_json(self, name, obj):
        with open(name + '.json', 'w') as f:
            json.dump(obj, f, indent=4)
