import requests
import json
import os

def main():
    proxy_url = "https://script.google.com/macros/s/AKfycby_yneEPDfmGGpGrZwCgEWt3KIQxZ_5V5LgX_8z9ItloS_Pg0p-SxsAqBW0OFdWa_WFog/exec"
    
    # Load credentials from config.json
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found.")
        return
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    google_key = config.get("GOOGLE_API_KEY", "")
    line_token = config.get("LINE_CHANNEL_ACCESS_TOKEN", "")
    
    print("--- Syncing Settings to Cloud Database ---")
    print(f"Google API Key to sync (masked): {google_key[:6]}...{google_key[-6:] if len(google_key) > 6 else ''}")
    print(f"LINE Token to sync (masked): {line_token[:6]}...{line_token[-6:] if len(line_token) > 6 else ''}")
    
    try:
        response = requests.post(
            proxy_url,
            json={
                "action": "save_settings",
                "settings": {
                    "GOOGLE_API_KEY": google_key,
                    "LINE_CHANNEL_ACCESS_TOKEN": line_token
                }
            },
            timeout=10
        )
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") == "settings_saved":
                print("🟢 Cloud database settings updated successfully!")
            else:
                print(f"🔴 Sync returned unexpected response: {res_json}")
        else:
            print(f"🔴 Sync request failed.")
    except Exception as e:
        print(f"🔴 Exception during sync: {e}")

if __name__ == "__main__":
    main()
