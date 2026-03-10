import json
import os
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(get_base_dir(), "config.json")

_default_config = {
    "ip": "127.0.0.1",
    "port": 9000,
    "chatbox_format": "{status} {name} - {artist}\n{mic} {lyrics}",
    "playback_provider": "Windows",
    "lyric_provider": "LRCLib"
}


def _load_config():
    try:
        with open(CONFIG_PATH, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return create_default_config()


def save_config(config_data):
    with open(CONFIG_PATH, 'w') as file:
        json.dump(config_data, file, indent=4)


def create_default_config():
    save_config(_default_config)
    return _default_config.copy()


_config = _load_config()


def get(key, default=None):
    return _config.get(key, default)


def set_config(key, value):
    _config[key] = value
    save_config(_config)
