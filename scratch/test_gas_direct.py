import requests
import json
import base64
import os

def main():
    proxy_url = "https://script.google.com/macros/s/AKfycby_yneEPDfmGGpGrZwCgEWt3KIQxZ_5V5LgX_8z9ItloS_Pg0p-SxsAqBW0OFdWa_WFog/exec"
    
    # Load app_icon.png as base64
    image_path = "app_icon.png"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return
        
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    base64_img = base64.b64encode(img_bytes).decode("utf-8")
    
    # Simple prompt to test
    payload = {
        "action": "generate_text",
        "prompt": "これはテストです。画像の内容を1行で日本語で説明してください。",
        "imageBase64": base64_img
    }
    
    print("Sending POST request to deployed GAS proxy...")
    try:
        # Note: Content-Type is text/plain to match Mobile app CORS bypass headers
        headers = {
            "Content-Type": "text/plain"
        }
        response = requests.post(proxy_url, data=json.dumps(payload), headers=headers, timeout=60)
        print(f"HTTP Status: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        
        # Sometimes GAS returns HTML wrap if errors occur, try json load
        try:
            res_data = response.json()
            print("🟢 JSON parsed successfully from response!")
            if "error" in res_data:
                print(f"🔴 GAS Error: {res_data['error']}")
            else:
                text_result = res_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if not text_result:
                    text_result = res_data.get("candidates", [{}])[0].get("part", {}).get("text", "")
                print(f"🟢 Success! Raw response snippet:\n{response.text[:200]}...")
                print(f"\n🟢 AI Text Output:\n{text_result}")
        except Exception as json_err:
            print(f"🔴 Response JSON Parse Error: {json_err}")
            print(f"Raw Response:\n{response.text[:500]}")
            
    except Exception as e:
        print(f"🔴 Exception: {e}")

if __name__ == "__main__":
    main()
