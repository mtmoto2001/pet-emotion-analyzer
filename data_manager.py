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

# --- 開発者コンソール用テレメトリ（ログ記録と世帯データ集約） ---
import glob
import datetime

USAGE_LOG_FILE = "usage_log.jsonl"

def log_usage(user_id, pet_name, pet_type, story_mode, genre, duration_ms, status, error_msg=None):
    # 日本時間（UTC+9）の現在時刻を取得
    tz_jst = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(tz_jst).strftime("%Y-%m-%d %H:%M:%S")
    
    log_data = {
        "timestamp": now,
        "user_id": user_id,
        "pet_name": pet_name,
        "pet_type": pet_type,
        "story_mode": story_mode,
        "genre": genre,
        "duration_ms": int(duration_ms) if duration_ms is not None else 0,
        "status": status,
        "error_msg": error_msg or ""
    }
    
    try:
        with open(USAGE_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Failed to write usage log: {e}")

def load_all_profiles():
    profiles = []
    # pet_profile_*.json にマッチするファイルをすべて検索
    files = glob.glob("pet_profile_*.json")
    for filepath in files:
        basename = os.path.basename(filepath)
        u_id = basename.replace("pet_profile_", "").replace(".json", "")
        # 本番デバッグ用などで user_id がない場合はスキップ
        if not u_id: continue
        
        profile_data = load_json(filepath)
        if profile_data and "name" in profile_data:
            profile_data["user_id"] = u_id
            # ファイルの更新日時を登録日時として取得
            try:
                mtime = os.path.getmtime(filepath)
                tz_jst = datetime.timezone(datetime.timedelta(hours=9))
                dt = datetime.datetime.fromtimestamp(mtime, tz_jst)
                profile_data["registered_at"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                profile_data["registered_at"] = "不明"
            profiles.append(profile_data)
            
    # 登録日時の降順でソート
    try:
        profiles.sort(key=lambda x: x.get("registered_at", ""), reverse=True)
    except:
        pass
    return profiles

def generate_user_id(owner_name, pin_code):
    """
    飼い主のおなまえと4桁のPINから一意の user_id を生成する。
    これにより、通常URLやPWA擬似ネイティブで起動した際でも、なまえとPINを入れるだけで
    完璧に同一の user_id に紐付くペット情報や思い出履歴を復元・永続化できる。
    """
    import hashlib
    if not owner_name or not pin_code:
        return None
    name_clean = str(owner_name).strip().replace(" ", "").replace("　", "")
    pin_clean = str(pin_code).strip()
    raw_str = f"{name_clean}_{pin_clean}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()[:12]
