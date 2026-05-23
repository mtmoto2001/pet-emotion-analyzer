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
    # 常に共通の config.json を返すようにし、APIキー等の漏洩防止と一元管理を実現します
    return CONFIG_FILE

def get_profile_filepath(user_id=None):
    return f"pet_profile_{user_id}.json" if user_id else PROFILE_FILE

def load_config(user_id=None): 
    config = load_json(CONFIG_FILE)
    # Streamlit Secrets が設定されている場合は最優先でマージして永続セキュリティを確保
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            sec_google = st.secrets.get("GOOGLE_API_KEY", "")
            sec_line = st.secrets.get("LINE_CHANNEL_ACCESS_TOKEN", "")
            if sec_google:
                config["GOOGLE_API_KEY"] = sec_google
            if sec_line:
                config["LINE_CHANNEL_ACCESS_TOKEN"] = sec_line
    except:
        pass
    return config

def save_config(l_token, google_key, user_id=None): 
    # 常にシステム共通の config.json に保存
    save_json(CONFIG_FILE, {"LINE_CHANNEL_ACCESS_TOKEN": l_token, "GOOGLE_API_KEY": google_key})

def load_profile(user_id=None): 
    return load_json(get_profile_filepath(user_id))

def save_profile(data, user_id=None): 
    save_json(get_profile_filepath(user_id), data)
