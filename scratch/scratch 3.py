import json

class JT_config:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config_data = self._load_config()

    def _load_config(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def _save_config(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.config_data, file, indent=4)

    def get_config(self, my_key):
        return self.config_data.get(my_key)

    def set_config(self, my_key, new_key_value):
        self.config_data[my_key] = new_key_value
        self._save_config()