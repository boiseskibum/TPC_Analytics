# jt_config.py
# purpose: ability to store configuration data (keys and values) into a file

import json

class JT_config:
    def __init__(self, file_path):
        self.file_path = file_path

    # get key value
    def get_config(self, my_key):
        try:
            with open(self.file_path, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        # if the key is not found then "None" is returned
        last_key_value = config.get(my_key, None)

        return last_key_value

    # set a key/value in the config file
    def set_config(self, my_key, new_key_value):
        my_return = False
        try:
            with open(self.file_path, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        config[my_key] = new_key_value
        with open(self.file_path, "w") as f:
            json.dump(config, f)
            my_return = True

        return my_return

########################################################

if __name__ == "__main__":
    # Test code
    file_path = 'config_testing.csv'  # Replace with the actual path to your CSV file

    # Create an instance of the DataProcessor
    config_obj = JT_config(file_path)

    print( f"test1: should be nothing/fail: {config_obj.get_config('abc')}")
    print( f"test2: stores a value: {config_obj.set_config('abc', 'abc_value1')}")
    print( f"test3: stores a value: {config_obj.set_config('abc2', 'abc_value2')}")

    print( f"test3: get abc2 value: {config_obj.get_config('abc2')}")
    print( f"test3: get def2 value, should fail: {config_obj.get_config('def2')}")


