from libs.async_eth_lib.utils.helpers import read_json, read_txt

MODULES_SETTINGS_FILE = read_json(['user_data', 'settings','modules_settings.json'])
PRIVATE_KEYS = read_txt(['user_data', 'input_data', 'private_keys.txt'])