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
        
    api_key = config.get("GOOGLE_API_KEY", "")
    print(f"Using Google API Key (masked): {api_key[:6]}...{api_key[-6:] if len(api_key) > 6 else ''}")
    
    # Fetch logs
    print("\n--- Fetching Logs from Google Sheets ---")
    try:
        response = requests.post(
            proxy_url,
            json={
                "action": "get_logs",
                "apiKey": api_key
            },
            timeout=10
        )
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            logs = response.json()
            if isinstance(logs, list):
                print(f"Successfully fetched {len(logs)} logs.")
                errors = [log for log in logs if log.get('status') != 'SUCCESS' or log.get('error_msg')]
                if errors:
                    print(f"\nFound {len(errors)} ERROR logs:")
                    for i, log in enumerate(reversed(errors)):
                        print(f"[{i+1}] {log.get('timestamp')} - User: {log.get('user_id')} - Pet: {log.get('pet_name')} - Status: {log.get('status')}")
                        print(f"    Error: {log.get('error_msg')}")
                
                success_logs = [log for log in logs if log.get('status') == 'SUCCESS']
                if success_logs:
                    print("\nRecent SUCCESS logs (newest first):")
                    for i, log in enumerate(reversed(success_logs[-10:])):
                        print(f"[{i+1}] {log.get('timestamp')} - User: {log.get('user_id')} - Pet: {log.get('pet_name')} - Duration: {log.get('duration_ms')} ms - StoryMode: {log.get('story_mode')} - Genre: {log.get('genre')}")
            else:
                print(f"Error parsing response: {logs}")
        else:
            print(f"Request failed: {response.text}")
    except Exception as e:
        print(f"Exception fetching logs: {e}")
        
if __name__ == "__main__":
    main()
