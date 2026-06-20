import requests
import json
import base64
import os

def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    key = config.get("GOOGLE_API_KEY")
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={key}"
    
    # Use app_icon.png as a test image
    image_path = "app_icon.png"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return
        
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    base64_img = base64.b64encode(img_bytes).decode("utf-8")
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "これはアプリのアイコンです。この画像に何が描かれているか、1行で日本語で説明してください。"},
                    {
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": base64_img
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2
        }
    }
    
    print("Sending multimodal request to Gemini API...")
    try:
        response = requests.post(gemini_url, json=payload, timeout=30)
        print(f"HTTP Status: {response.status_code}")
        if response.status_code == 200:
            res_data = response.json()
            text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"🟢 Success! Response: {text}")
        else:
            print(f"🔴 Failure: {response.text}")
    except Exception as e:
        print(f"🔴 Exception: {e}")

if __name__ == "__main__":
    main()
