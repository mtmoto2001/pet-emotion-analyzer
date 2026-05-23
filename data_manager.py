import os
import json

CONFIG_FILE = "config.json"
PROFILE_FILE = "pet_profile.json"

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_config_filepath(user_id=None):
    return f"config_{user_id}.json" if user_id else CONFIG_FILE

def get_profile_filepath(user_id=None):
    return f"pet_profile_{user_id}.json" if user_id else PROFILE_FILE

def load_config(user_id=None): 
    return load_json(get_config_filepath(user_id))

def save_config(l_token, google_key, user_id=None): 
    save_json(get_config_filepath(user_id), {"LINE_CHANNEL_ACCESS_TOKEN": l_token, "GOOGLE_API_KEY": google_key})

def load_profile(user_id=None): 
    return load_json(get_profile_filepath(user_id))

def save_profile(data, user_id=None): 
    save_json(get_profile_filepath(user_id), data)
