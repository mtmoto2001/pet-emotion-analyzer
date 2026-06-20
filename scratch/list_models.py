import requests
import json

def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    key = config.get("GOOGLE_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    
    print("Listing available models for this API key...")
    try:
        response = requests.get(url, timeout=10)
        print(f"HTTP Status: {response.status_code}")
        if response.status_code == 200:
            res_data = response.json()
            models = res_data.get("models", [])
            print(f"Found {len(models)} models:")
            for m in models:
                name = m.get("name")
                display_name = m.get("displayName")
                print(f"- {name} ({display_name})")
        else:
            print(f"🔴 Failure: {response.text}")
    except Exception as e:
        print(f"🔴 Exception: {e}")

if __name__ == "__main__":
    main()
