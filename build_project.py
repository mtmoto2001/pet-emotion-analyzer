import os

# 1. data_manager.py の生成
with open("data_manager.py", "w", encoding="utf-8") as f:
    f.write('''import os
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

def load_config(): return load_json(CONFIG_FILE)
def save_config(g_key, l_token): save_json(CONFIG_FILE, {"GOOGLE_API_KEY": g_key, "LINE_CHANNEL_ACCESS_TOKEN": l_token})

def load_profile(): return load_json(PROFILE_FILE)
def save_profile(data): save_json(PROFILE_FILE, data)
''')

# 2. line_api.py の生成
with open("line_api.py", "w", encoding="utf-8") as f:
    f.write('''import requests

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
                "text": f"🎨 【ChatGPT (DALL-E 3) 専用画像生成プロンプト】\\n\\n以下の英文をそのままコピーしてChatGPT Plusに貼り付けてください：\\n\\n{image_prompt}"
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
''')

# 3. ai_core.py の生成
with open("ai_core.py", "w", encoding="utf-8") as f:
    f.write('''import requests
import json
import base64

def run_ai_factory(google_key, pet_info, uploaded_file):
    """Gemini 2.5 Flashを使用してマルチモーダル心情分析とストーリー生成を行う"""
    if not google_key or google_key == "YOUR_GOOGLE_API_KEY":
        return None, "Google APIキーが設定されていません。"

    file_bytes = uploaded_file.read()
    base64_data = base64.b64encode(file_bytes).decode("utf-8")
    mime_type = uploaded_file.type

    prompt_text = f"""
    あなたは、大切なペットの視点に完全に憑依し、家族への愛を一切の妥協なく美しい日本語で翻訳する「最高峰のメモリアル作家」です。
    添付された写真または動画の要素をディープに解析し、以下の【ペットの厳密な基本情報】を100%確実に加味したストーリーを執筆してください。

    【ペットの厳密な基本情報】
    ・名前: {pet_info['name']}
    ・種別: {pet_info['pet_type']}
    ・品種（犬種/猫種）: {pet_info['breed']}
    ・毛色/特徴: {pet_info['color']}
    ・性別: {pet_info['gender']}
    ・正確な年齢: {pet_info['age_display']}
    ・コアな性格傾向: {pet_info['personality']}
    ・性格の補足・詳細: {pet_info['personality_detail']}
    ・飼い主の呼び方: {pet_info['owner_call']}

    【執筆指示】
    1. 翻訳調の不自然な日本語は完全に排除し、瑞々しく涙が溢れるような美しい文体で執筆すること。
    2. 年齢（幼少期、成熟期、シニア期）に応じた適切な語り口調にすること。
    3. 飼い主を指す言葉、または語りかける際は必ず{pet_info['owner_call']}という呼び方を使用すること。

    【出力フォーマット】必ず以下のJSONのみを出力。
    {{
        "analysis": "写真_動画から読み取った、{pet_info['name']}ちゃんのリアルな心情分析（日本語、200文字程度）",
        "story": "スマホのLINE画面で読んだ時に最も感動するロングストーリー（日本語、800〜1000文字程度）。2〜3行ごとに必ず空行（改行）を挟むこと。",
        "image_prompt": "この物語の世界観を美しく表現した、ChatGPT(DALL-E 3)専用の最高クオリティの画像生成用英語プロンプト。水彩画、絵本風タッチの指定（Water color illustration, warm and soft tones, picture book style）を含めること。"
    }}
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {"inlineData": {"mimeType": mime_type, "data": base64_data}}
            ]
        }],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={google_key}"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload)
        result_json = response.json()
        
        raw_output = result_json['candidates'][0]['content']['parts'][0]['text']
        data = json.loads(raw_output)
        
        line_story_format = f"🐾 【{pet_info['name']}ちゃんの心情分析】\\n{data['analysis']}\\n\\n💌 【愛を伝えるメモリアルストーリー】\\n{data['story']}"
        return line_story_format, data['image_prompt']
    except Exception as e:
        return None, f"AI生成エラー: {e}"
''')

# 4. app.py の生成（UIメインコントロール）
with open("app.py", "w", encoding="utf-8") as f:
    f.write('''import streamlit as st
import datetime
import os
import data_manager
import ai_core
import line_api

# --- ページ設定 ---
st.set_page_config(page_title="Pet Memorial AI Factory", page_icon="🐾", layout="wide")

# --- カスタムCSSの注入 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Noto Sans JP', sans-serif; }
    .main-title { background: linear-gradient(45deg, #FF7B93, #FFB88C); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 2.8rem; margin-bottom: 0.2rem; }
    .sub-title { color: #A0AEC0; font-size: 1.1rem; margin-bottom: 2rem; }
    div[data-testid="stForm"] { border: 1px solid #2D3748 !important; border-radius: 16px !important; background-color: #1A202C !important; padding: 2rem !important; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); }
    .line-preview-box { background-color: #111827; border-left: 4px solid #10B981; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; color: #E2E8F0; white-space: pre-wrap; }
    .stButton>button { background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%) !important; color: white !important; font-weight: bold !important; border: none !important; border-radius: 8px !important; padding: 0.6rem 2rem !important; transition: all 0.3s ease !important; width: 100% !important; }
    .stButton>button:hover { transform: translateY(-2px) !important; box-shadow: 0 10px 15px -3px rgba(118, 75, 162, 0.4) !important; }
</style>
""", unsafe_allow_html=True)

# データの読み込み
saved_config = data_manager.load_config()
saved_profile = data_manager.load_profile()

st.markdown('<p class="main-title">🐾 Pet Memorial AI Factory</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">マルチモーダル心情分析 ➔ 絆を紡ぐLINE配信自動化システム</p>', unsafe_allow_html=True)

# --- ⚙️ サイドバー：システム設定 & アコーディオン情報修正 ---
with st.sidebar:
    st.markdown("### 🛠️ 工場・基盤管理")
    input_google = st.text_input("🔑 Google AI Studio Key", value=saved_config.get("GOOGLE_API_KEY", ""), type="password")
    input_line = st.text_input("💬 LINE Access Token", value=saved_config.get("LINE_CHANNEL_ACCESS_TOKEN", ""), type="password")
    
    if st.button("💾 クラウド鍵を固定保存"):
        data_manager.save_config(input_google, input_line)
        st.success("システム設定を保存しました。")
        st.rerun()

    st.write("---")
    st.markdown("### 📡 配信コントロール")
    line_switch = st.checkbox("🟢 LINEへ一斉配信を許可（ON）", value=False)
    
    # ② ペット情報がすでに存在する場合、サイドバーのアコーディオンに格納
    if saved_profile:
        st.write("---")
        with st.expander("📝 ペットの基本情報を修正する"):
            st.info("情報を変更して「プロファイルを更新」を押してください。")
            edit_name = st.text_input("名前", value=saved_profile.get("name", ""), key="ed_name")
            edit_type = st.selectbox("種類", ["犬", "猫"], index=0 if saved_profile.get("pet_type", "犬") == "犬" else 1, key="ed_type")
            edit_breed = st.text_input("品種", value=saved_profile.get("breed", ""), key="ed_breed")
            edit_color = st.text_input("毛色", value=saved_profile.get("color", ""), key="ed_color")
            edit_gender = st.radio("性別", ["男の子", "女の子"], index=0 if saved_profile.get("gender", "男の子") == "男の子" else 1, key="ed_gender", horizontal=True)
            edit_owner = st.text_input("飼い主の呼び方", value=saved_profile.get("owner_call", "パパ"), key="ed_owner")
            
            if st.button("💾 プロファイルを更新"):
                updated_data = saved_profile.copy()
                updated_data.update({"name": edit_name, "pet_type": edit_type, "breed": edit_breed, "color": edit_color, "gender": edit_gender, "owner_call": edit_owner})
                data_manager.save_profile(updated_data)
                st.success("プロファイルを更新しました。")
                st.rerun()

GOOGLE_API_KEY = input_google if input_google else saved_config.get("GOOGLE_API_KEY", "")
LINE_CHANNEL_ACCESS_TOKEN = input_line if input_line else saved_config.get("LINE_CHANNEL_ACCESS_TOKEN", "")

# ② 【最重要】初回起動時、またはプロファイルがない場合にポップアップ（ダイアログ）を起動
@st.dialog("🐾 ペットの基本プロファイル登録")
def show_profile_dialog():
    st.write("アプリの利用を始める前に、ペットの基本情報を教えてください。この情報はローカルに安全に永続化されます。")
    p_name = st.text_input("名前", value="ベル")
    p_type = st.selectbox("動物の種別", ["犬", "猫"])
    p_breed = st.text_input("犬種・猫種", value="ミニチュアダックスフンド")
    p_color = st.text_input("毛色・視覚的特徴", value="レッド")
    p_gender = st.radio("性別", ["男の子", "女の子"], horizontal=True)
    p_owner_call = st.text_input("飼い主の呼び方（パパ、ママ等）", value="パパ")
    
    st.write("誕生年月（年齢最適化ロジック用）")
    c_year = datetime.datetime.now().year
    p_birth_y = st.selectbox("誕生年", list(range(c_year, c_year-25, -1)), index=2)
    p_birth_m = st.selectbox("誕生月", list(range(1, 13)), index=0)
    
    personality_options = ["元気いっぱいでやんちゃ", "甘えん坊で寂しがり屋", "おっとりマイペース", "賢く、人間の言葉を理解しようとする", "臆病だけど優しい"]
    p_pers = st.selectbox("基本の性格傾向", personality_options)
    p_pers_detail = st.text_area("具体的なエピソード・行動詳細", value="お気に入りのおもちゃをくわえて、得意げに部屋中を走り回っていたこと。")
    
    if st.button("💾 この内容で初期プロファイルを保存"):
        # 年齢の自動計算
        current_date = datetime.date(2026, 5, 16)
        birth_date = datetime.date(p_birth_y, p_birth_m, 1)
        total_months = (current_date.year - birth_date.year) * 12 + current_date.month - birth_date.month
        if total_months < 0: age_display = "生後0ヶ月"
        elif total_months < 12: age_display = f"子犬/子猫期（生後 {total_months} ヶ月）"
        else: age_display = f"成犬/成猫期（ {total_months // 12} 歳 {total_months % 12} ヶ月）"

        profile_data = {
            "name": p_name, "pet_type": p_type, "breed": p_breed, "color": p_color,
            "gender": p_gender, "birth_y": p_birth_y, "birth_m": p_birth_m,
            "personality": p_pers, "personality_detail": p_pers_detail, "owner_call": p_owner_call,
            "age_display": age_display
        }
        data_manager.save_profile(profile_data)
        st.success("プロファイルを安全に永続化しました！")
        st.rerun()

# データがなければダイアログを強制表示
if not saved_profile:
    show_profile_dialog()

# --- 🏢 メイン画面（機能美を極めたすっきりレイアウト） ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 🎬 メディアの解析＆実行")
    if saved_profile:
        st.info(f"✨ 現在の対象: **{saved_profile['name']}ちゃん** ({saved_profile['breed']} / {saved_profile['age_display']})")
    
    with st.form(key="media_submit_form"):
        uploaded_file = st.file_uploader("愛犬・愛猫の写真、または動画（.mp4）をドラッグ＆ドロップ", type=["jpg", "jpeg", "png", "mp4"])
        submit_button = st.form_submit_button(label="✨ パイプラインを実行（ストーリー自動錬成）")
        
    if submit_button:
        if uploaded_file is None:
            st.warning("解析用のメディアファイルを選択してください。")
        elif not saved_profile:
            st.error("ペットのプロファイルが設定されていません。画面をリロードして登録してください。")
        else:
            for key in ['display_story', 'display_prompt', 'line_status']:
                if key in st.session_state: del st.session_state[key]
            
            story_res, prompt_res = ai_core.run_ai_factory(GOOGLE_API_KEY, saved_profile, uploaded_file)
            
            if story_res:
                st.session_state['display_story'] = story_res
                st.session_state['display_prompt'] = prompt_res
                
                if line_switch:
                    status = line_api.send_to_line_broadcast(LINE_CHANNEL_ACCESS_TOKEN, story_res, prompt_res)
                    st.session_state['line_status'] = status
                else:
                    st.session_state['line_status'] = "ℹ️ 安全モード：LINE一斉配信はOFFです。ローカル環境のみに出力しました。"
                st.rerun()

with col2:
    st.markdown("### 💎 生成されたメモリアル・アセット")
    
    if 'line_status' in st.session_state:
        st.info(st.session_state['line_status'])
        
    if 'display_prompt' in st.session_state:
        st.write("🎨 **ChatGPT (DALL-E 3) 連携用プロンプト・スタジオ**")
        st.caption("以下のボックスをトリプルクリック（または全選択）してコピーし、ChatGPTに投げてアートを生成してください。")
        st.text_area(label="DALL-E 3 Prompt (Auto Generated)", value=st.session_state['display_prompt'], height=100, key="dalle_prompt_view")
        
    if 'display_story' in st.session_state:
        st.write("---")
        st.write("📱 **LINE配信メッセージ・シミュレーター**")
        st.markdown(f'<div class="line-preview-box">{st.session_state["display_story"]}</div>', unsafe_allow_html=True)
    else:
        st.info("左側でメディアをアップロードして実行すると、ここにデザインされたアセット群が瞬時に展開されます。")

st.write("---")
st.caption("Powered by Gemini 2.5 Flash & DALL-E 3 Architecture")
''')

print("🎉 すべてのファイル（app.py, ai_core.py, line_api.py, data_manager.py）が美しく分割生成されました！")
