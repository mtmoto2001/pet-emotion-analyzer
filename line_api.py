import requests

def send_to_line_broadcast(token, story_text, image_prompt):
    """LINE公式アカウントのMessaging APIを使用して一斉配信する"""
    if not token or token == "YOUR_LINE_CHANNEL_ACCESS_TOKEN":
        return "⚠️ LINEアクセストークンが未設定のため、配信をスキップしました。"

    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "messages": [
            {"type": "text", "text": story_text},
            {
                "type": "text",
                "text": f"🎨 【ChatGPT (DALL-E 3) 専用画像生成プロンプト】\n\n以下の英文をそのままコピーしてChatGPT Plusに貼り付けてください：\n\n{image_prompt}"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return "🚀 LINE公式アカウントのメンバー全員へ同時に美しく配信されました！"
        else:
            return f"❌ LINE配信失敗（エラーコード: {response.status_code}）: {response.text}"
    except Exception as e:
        return f"❌ LINE通信障害: {e}"
