import streamlit as st
import datetime
import os
import uuid
import base64
import data_manager
import ai_core
import streamlit.components.v1 as components

@st.cache_data
def get_loading_video_base64():
    video_path = os.path.join(os.path.dirname(__file__), "loading_animation.mp4")
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# --- ページ設定 ---
st.set_page_config(page_title="うちのコ日常アルバム - Pet Daily AI", page_icon="🐾", layout="wide")

# --- ユーザーID（世帯ID）の自動生成とクエリパラメータ処理 ---
if "user_id" not in st.query_params:
    new_id = str(uuid.uuid4())[:8]
    st.query_params["user_id"] = new_id
    st.rerun()

user_id = st.query_params["user_id"]

# --- LocalStorage からのペット情報復元処理 ---
if "restore_profile" in st.query_params:
    import urllib.parse
    import json
    try:
        raw_val = st.query_params["restore_profile"]
        profile_json = urllib.parse.unquote(raw_val)
        profile_data = json.loads(profile_json)
        if profile_data and "name" in profile_data:
            # サーバー側に保存してセッションを復元
            data_manager.save_profile(profile_data, user_id)
            st.query_params.pop("restore_profile")
            st.rerun()
    except Exception as e:
        pass

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap');
    
    /* ベースリセット ＆ スマートフォン最適化 */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Noto Sans JP', sans-serif;
        background-color: #0F172A; /* 深みのあるロイヤルダークブルー */
    }
    
    /* プレミアムグラデーションタイトル */
    .main-title {
        background: linear-gradient(45deg, #FF7B93, #FFB88C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.2rem !important; /* スマホで折れ曲がらないよう少し縮小 */
        margin-bottom: 0.1rem;
        text-align: center;
    }
    .sub-title {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        text-align: center;
        line-height: 1.5;
    }
    
    /* ガラスモーフィズム・透過角丸プレミアムカード */
    .status-card {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 1.2rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }
    
    /* 超高コントラスト読書 preview ボックス (スマホ最適化) */
    .line-preview-box { 
        background-color: #0F172A !important; 
        border-left: 5px solid #FF7B93 !important; 
        border-radius: 12px; 
        padding: 1.2rem; 
        margin-top: 0.8rem; 
        color: #F8FAFC !important; 
        white-space: pre-wrap; 
        font-size: 1.02rem; 
        line-height: 1.8;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.5), 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    /* 入力フォームのスマホ最適化 */
    div[data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.55) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        padding: 1.5rem !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    
    /* モバイルの親指にフィットする大きめのタッチ領域 */
    .stButton>button {
        background: linear-gradient(135deg, #FF7B93 0%, #FFB88C 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.9rem 2rem !important;
        transition: transform 0.1s ease, box-shadow 0.2s ease !important;
        width: 100% !important;
        font-size: 1.1rem !important;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(255, 123, 147, 0.3);
    }
    .stButton>button:active {
        transform: scale(0.98);
        box-shadow: 0 2px 8px rgba(255, 123, 147, 0.2);
    }
    
    /* 全画面ローディングオーバーレイ */
    .full-screen-loader {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(15, 23, 42, 0.97); /* 深みのあるロイヤルダーク背景で100%覆う */
        z-index: 999999 !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        box-sizing: border-box;
        animation: loaderFadeIn 0.3s ease-out forwards;
    }
    .loader-card {
        text-align: center;
        max-width: 480px;
        width: 100%;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 2rem;
        border-radius: 24px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        backdrop-filter: blur(15px);
    }
    .loading-video {
        width: 100%;
        max-width: 320px;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        border: 2px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 1.5rem;
    }
    @keyframes loaderFadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* モバイルでの左右パディングの強制縮小 */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 1.5rem !important;
        }
        .main-title {
            font-size: 1.9rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 使い方チュートリアルダイアログの定義 ---
@st.dialog("📖 うちのコ日常アルバム 使い方ガイド")
def show_tutorial_dialog():
    st.write("アプリの使い方を紙芝居形式で分かりやすくガイドします。上のタブを切り替えてお読みください🐾")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👋 ようこそ！", "💡 基本の使い方", "🎨 4コマ漫画の作り方", "📱 アプリアイコン化"])
    
    with tab1:
        st.markdown("""
        ### ようこそ！『うちのコ日常アルバム』へ 🐾
        このアプリは、愛するペットのお気に入りの写真から**「ペットの本当の気持ち（心の声）」**や**「特別な思い出ショートストーリー」**を最先端AI（Gemini）がつむぐアルバムアプリです。
        
        さらに、そのストーリーをベースにした**「超高品質な4コマ漫画」**をChatGPTで作成できる魔法のプロンプトを生成します！
        
        まずは右上の「基本の使い方」タブをタップしてみましょう ➡
        """)
        st.info("💡 登録されたペットの性格や年齢に合わせて、AIが世界に一つだけのストーリーを執筆します。")
        
    with tab2:
        st.markdown("""
        ### 💡 アプリの基本の使い方（簡単3ステップ）
        
        1. **📸 写真のアップロード**:
           画面の左側で、おうちのコのお気に入りの写真（JPEG/PNG形式）を1枚アップロードします。
        2. **📚 小説スタイルの選択**:
           客観的に描く『絵本小説風（6つのジャンル選択可能）』か、ペット本人が語りかける『おしゃべり風』から選択します。
        3. **⚡ ストーリーをつくる**:
           「思い出のストーリーをつくる」ボタンを押して数十秒待つと、画面右側に心情分析と小説が完成します！
        """)
        st.success("✨ 動画アップロードには非対応です。お写真をお使いください！")
        
    with tab3:
        st.markdown("""
        ### 🎨 4コマ漫画のつくり方（ChatGPT連携）
        ストーリー生成後に画面右側に出力されるプロンプトを使い、ChatGPTで最高品質の4コマ漫画を生成します。
        
        1. **📋 コピーボタンをタップ**:
           プロンプト欄のすぐ下にある **「プロンプトをコピーする」** ボタンをタップします（クリップボードに記憶されます）。
        2. **🚀 ChatGPTを起動**:
           その下にある **「ChatGPTで4コマ漫画生成」** ボタンをタップして、ChatGPT（DALL-E 3）の画面を開きます。
        3. **📝 貼り付けて送信するだけ！**:
           ChatGPTのチャット入力欄にコピーしたプロンプトを**そのまま貼り付けて送信**してください。
           自動的に、あなたのコの特徴や表情を100%引き継いだ、感動的な4コマ漫画が目の前で描き出されます！
        """)
        st.warning("⚠️ ChatGPT側で画像が生成されるまで1〜2分かかります。そのまま楽しみにお待ちください！")
        
    with tab4:
        st.markdown("""
        ### 📱 スマートフォンのホーム画面にアプリアイコンを作る方法
        このWebアプリを、スマホのホーム画面にアプリアイコンとして登録することで、SafariやChromeの枠が消えて**本物のネイティブアプリ同様の全画面表示**で快適に起動できるようになります！
        
        * **🍎 iPhone (Safariの場合)**:
          1. Safariでこのアプリを開きます。
          2. 下部の **「共有ボタン」**（四角から矢印が出ているアイコン）をタップします。
          3. **「ホーム画面に追加」** をタップして、右上の「追加」を押します。
        * **🤖 Android (Chromeの場合)**:
          1. Chromeでこのアプリを開きます。
          2. 右上の **「三点リーダー（メニュー）」** をタップします。
          3. **「ホーム画面に追加」** または **「アプリをインストール」** をタップします。
        """)
        st.info("🐾 ホーム画面に追加すると、次回からホーム画面の可愛い肉球アイコン（🐾）をタップするだけで一瞬で起動します！")

    if st.button("ガイドを閉じる", key="btn_close_tutorial", use_container_width=True):
        st.rerun()

# --- データの読み込み ---
saved_config = data_manager.load_config(user_id)
saved_profile = data_manager.load_profile(user_id)

# サーバー側にプロフィールが無い場合、ブラウザの LocalStorage からの復元を試みるJSを埋め込み
if not saved_profile:
    restore_js = """
    <script>
    try {
        const profile = localStorage.getItem("pet_profile");
        if (profile) {
            const parsed = JSON.parse(profile);
            if (parsed && parsed.name) {
                const encoded = encodeURIComponent(profile);
                const parentUrl = new URL(window.parent.location.href);
                if (!parentUrl.searchParams.has("restore_profile")) {
                    parentUrl.searchParams.set("restore_profile", encoded);
                    window.parent.location.href = parentUrl.toString();
                }
            }
        }
    } catch(e) {
        console.error("LocalStorage restore failed:", e);
    }
    </script>
    """
    components.html(restore_js, height=0, width=0)

# --- 登録完了後に自動でチュートリアルを表示する処理 ---
if st.session_state.get("show_tutorial_after_reg"):
    st.session_state.pop("show_tutorial_after_reg")
    show_tutorial_dialog()

st.markdown('<p class="main-title">🐾 うちのコ日常アルバム</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">お気に入りの写真から、愛犬・愛猫の心の声と特別な4コマストーリーをつむぐアルバムアプリ</p>', unsafe_allow_html=True)

# --- LocalStorageへの保存トリガーJSの出力 ---
if "save_profile_to_localstorage" in st.session_state:
    profile_to_save = st.session_state.pop("save_profile_to_localstorage")
    import json
    save_js = f"""
    <script>
    try {{
        localStorage.setItem("pet_profile", `{json.dumps(profile_to_save, ensure_ascii=False)}`);
    }} catch(e) {{
        console.error("LocalStorage save failed:", e);
    }}
    </script>
    """
    components.html(save_js, height=0, width=0)

with st.sidebar:
    # 📖 使い方ガイドボタンをサイドバーの最上部に設置
    st.markdown("### 📖 ナビゲーション")
    if st.button("📖 アプリの使い方（チュートリアル）", key="btn_show_tutorial_global", use_container_width=True):
        show_tutorial_dialog()
    
    st.write("---")

    # 管理者用パラメータチェック (?admin=true がある場合のみシステム設定を表示)
    is_admin = st.query_params.get("admin") == "true"
    
    if is_admin:
        st.markdown("### 🛠️ システム設定（管理者専用）")
        input_line = st.text_input("💬 LINEアクセストークン", value=saved_config.get("LINE_CHANNEL_ACCESS_TOKEN", ""), type="password", key="root_lt_id")
        input_google = st.text_input("🔑 Google Gemini APIキー", value=saved_config.get("GOOGLE_API_KEY", ""), type="password", key="root_gk_id")
        
        if st.button("💾 設定を保存する", key="btn_save_root_config"):
            data_manager.save_config(input_line, input_google)
            st.success("設定を保存しました。")
            st.rerun()

        st.write("---")
        st.markdown("### 📡 送信設定")
        line_switch = st.checkbox("🟢 LINEに自動で送る", value=False, key="root_switch_ls_id")
        st.write("---")
    else:
        # 一般ユーザーはLINE自動送信はOFF固定、APIキーはSecretsから読み込んだ値をバインド
        input_line = saved_config.get("LINE_CHANNEL_ACCESS_TOKEN", "")
        input_google = saved_config.get("GOOGLE_API_KEY", "")
        line_switch = False

    if saved_profile:
        st.markdown("### 📝 登録されているペットの情報")
        st.markdown(f"""
        <div class="status-card">
        🐶 <b>お名前:</b> {saved_profile.get('name')}<br>
        🏷️ <b>種類:</b> {saved_profile.get('pet_type')} ({saved_profile.get('breed')})<br>
        ⏳ <b>年齢:</b> {saved_profile.get('age_display')}<br>
        👤 <b>飼い主さんの呼び方:</b> {saved_profile.get('owner_call')}
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📝 登録情報を変更する"):
            st.info("情報を変更して「登録情報を更新する」を押してください。")
            edit_name = st.text_input("名前", value=saved_profile.get("name", ""), key="ed_name")
            edit_type = st.selectbox("種類", ["犬", "猫"], index=0 if saved_profile.get("pet_type", "犬") == "犬" else 1, key="ed_type")
            edit_breed = st.text_input("品種", value=saved_profile.get("breed", ""), key="ed_breed")
            edit_color = st.text_input("毛色", value=saved_profile.get("color", ""), key="ed_color")
            edit_gender = st.radio("性別", ["男の子", "女の子"], index=0 if saved_profile.get("gender", "男の子") == "男の子" else 1, key="ed_gender", horizontal=True)
            edit_owner = st.text_input("飼い主さんの呼び方", value=saved_profile.get("owner_call", "パパ"), key="ed_owner")
            
            if st.button("💾 登録情報を更新する"):
                updated_data = saved_profile.copy()
                updated_data.update({"name": edit_name, "pet_type": edit_type, "breed": edit_breed, "color": edit_color, "gender": edit_gender, "owner_call": edit_owner})
                data_manager.save_profile(updated_data, user_id)
                st.session_state["save_profile_to_localstorage"] = updated_data
                st.success("ペット情報を更新しました。")
                st.rerun()

    # --- 誤操作防止のため、クリアボタンをサイドバーの最下部に移動 ---
    st.write("---")
    st.markdown("### ⚙️ 管理・クリア")
    if st.button("🗑️ 表示をクリアする（過去の生成結果を消去）", key="sidebar_clear_btn_v7"):
        st.session_state.pop('display_story', None)
        st.session_state.pop('display_feelings', None)
        st.session_state.pop('display_prompt', None)
        st.session_state.pop('line_status', None)
        st.success("表示データをクリアしました。")
        st.rerun()

LINE_CHANNEL_ACCESS_TOKEN = input_line if input_line else saved_config.get("LINE_CHANNEL_ACCESS_TOKEN", "")
GOOGLE_API_KEY = input_google if input_google else saved_config.get("GOOGLE_API_KEY", "")

@st.dialog("🐾 はじめてのペット登録")
def show_profile_dialog():
    st.write("アプリを始める前に、まずはうちのコのことを教えてください。情報はローカルに安全に保存されます。")
    p_name = st.text_input("名前", value="ベル")
    p_type = st.selectbox("動物の種別", ["犬", "猫"])
    p_breed = st.text_input("犬種・猫種", value="ミニチュアダックスフンド")
    p_color = st.text_input("毛色・視覚的特徴", value="レッド")
    p_gender = st.radio("性別", ["男の子", "女の子"], horizontal=True)
    p_owner_call = st.text_input("飼い主さんの呼び方（パパ、ママなど）", value="パパ")
    
    st.write("お誕生日（年齢の自動判定に使用します）")
    c_year = datetime.datetime.now().year
    p_birth_y = st.selectbox("誕生年", list(range(c_year, c_year-25, -1)), index=2)
    p_birth_m = st.selectbox("誕生月", list(range(1, 13)), index=0)
    
    personality_options = ["元気いっぱいでやんちゃ", "甘えん坊で寂しがり屋", "おっとりマイペース", "賢く、人間の言葉を理解しようとする", "臆病だけど優しい"]
    p_pers = st.selectbox("基本の性格傾向", personality_options)
    p_pers_detail = st.text_area("具体的なエピソード・行動詳細", value="お気に入りのおもちゃをくわえて、得意げに部屋中を走り回っていたこと。")
    
    if st.button("💾 この内容で登録する"):
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
        data_manager.save_profile(profile_data, user_id)
        st.session_state["save_profile_to_localstorage"] = profile_data
        st.session_state["show_tutorial_after_reg"] = True
        st.success("登録が完了しました！使い方ガイドを表示します。")
        st.rerun()

# データがなければダイアログを強制表示
if not saved_profile:
    show_profile_dialog()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 🎬 思い出の写真とストーリーの選択")
    
    with st.form(key="secure_capsule_form_v7"):
        story_mode = st.radio("📝 ストーリーのスタイルを選んでください", ["絵本小説風（客観的な視点から）", "おしゃべり風（うちのコの一人称で）"], horizontal=True, key="sm_sel_v7")
        
        # --- 小説ジャンルの選択プルダウンを追加 ---
        genre = "ほのぼの日常風"
        if story_mode == "絵本小説風（客観的な視点から）":
            genre = st.selectbox(
                "📚 小説のジャンルを選んでください",
                ["ほのぼの日常風", "恋愛小説風", "冒険小説風", "ミステリー（世にも奇妙な物語風）", "異世界転生風", "学園小説風"],
                index=0,
                key="novel_genre_selectbox"
            )
            
        uploaded_file = st.file_uploader("愛犬・愛猫の写真ファイルをアップロードしてください（.jpg / .jpeg / .png）", type=["jpg", "jpeg", "png"], key="fu_native_v7")
        submit_button = st.form_submit_button(label="⚡️ 思い出のストーリーをつくる")
    
    p_bar = st.empty()
    p_text = st.empty()
    
    if submit_button:
        # 新しい処理を始める前に、過去の結果をクリアする
        st.session_state.pop('display_story', None)
        st.session_state.pop('display_feelings', None)
        st.session_state.pop('display_prompt', None)
        
        if not GOOGLE_API_KEY:
            if is_admin:
                st.error("Google Gemini APIキーが未設定です。上の管理者設定から登録して保存してください。")
            else:
                st.error("システム設定エラーが発生しました。時間を置いて再度お試しいただくか、開発者にお問い合わせください🐾")
        elif uploaded_file is None:
            st.warning("思い出の写真ファイルを選んでアップロードしてください。")
        elif not saved_profile:
            st.error("ペットの情報が登録されていません。")
        else:
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            
            # 複数スマホからの同時利用時でもファイル名衝突が起きないUUID割り当て
            _, ext = os.path.splitext(uploaded_file.name)
            temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}{ext}")
            
            p_bar.progress(10)
            p_text.info("📥 思い出のファイルを準備しています...")
            
            with open(temp_file_path, "wb") as f:
                while True:
                    chunk = uploaded_file.read(4096)
                    if not chunk: break
                    f.write(chunk)
            
            try:
                loading_placeholder = st.empty()
                with loading_placeholder.container():
                    video_base64 = get_loading_video_base64()
                    st.markdown(f"""
                    <div class="full-screen-loader">
                      <div class="loader-card">
                        <video class="loading-video" autoplay loop muted playsinline>
                          <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                          Your browser does not support the video tag.
                        </video>
                        <h3 style="color: #FF7B93; margin-top: 0.5rem; font-weight: bold; font-size: 1.4rem;">心を込めて執筆中...🐾</h3>
                        <p style="color: #94A3B8; font-size: 0.95rem; line-height: 1.6; margin-top: 0.8rem; margin-bottom: 0;">
                          AIが思い出の写真から本当の気持ちを読み解き、特別なショートストーリーを創作しています。<br>10〜30秒ほど楽しみにお待ちください。
                        </p>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                import time
                start_time = time.time()
                feelings_res, story_res, prompt_res = ai_core.run_ai_factory(GOOGLE_API_KEY, saved_profile, temp_file_path, story_mode, genre, p_bar, p_text)
                duration_ms = (time.time() - start_time) * 1000
                
                if feelings_res:
                    st.session_state['display_feelings'] = feelings_res
                    st.session_state['display_story'] = story_res
                    st.session_state['display_prompt'] = prompt_res
                    
                    # ログの記録 (成功)
                    data_manager.log_usage(
                        user_id=user_id,
                        pet_name=saved_profile.get("name", "不明"),
                        pet_type=saved_profile.get("pet_type", "不明"),
                        story_mode=story_mode,
                        genre=genre if story_mode == "絵本小説風（客観的な視点から）" else "おしゃべり風",
                        duration_ms=duration_ms,
                        status="SUCCESS"
                    )
                    
                    uploaded_file.seek(0)
                    st.session_state['display_image'] = uploaded_file.read()
                    st.session_state['display_mime'] = uploaded_file.type
                    
                    # LINE自動送信は管理者セッション（is_admin=True）かつスイッチONの場合のみ実行
                    if is_admin and line_switch:
                        # LINE配信用テキストの構築
                        line_text = f"🐾 【{saved_profile['name']}ちゃんの日常心情分析】\n{feelings_res}\n\n📖 【思い出ストーリー】\n{story_res}\n\n🎨 【GPT用4コマ漫画生成プロンプト】\n{prompt_res}"
                        status = line_api.send_to_line_broadcast(LINE_CHANNEL_ACCESS_TOKEN, line_text, prompt_res)
                        st.session_state['line_status'] = status
                    elif is_admin:
                        st.session_state['line_status'] = "ℹ️ LINE自動送信はOFFです。ローカル画面のみに出力しました。"
                    else:
                        # 一般ユーザーの場合はLINEステータスを出さず、メッセージ自体を格納しない
                        st.session_state.pop('line_status', None)
                else:
                    st.error(prompt_res)
                    # ログの記録 (失敗)
                    data_manager.log_usage(
                        user_id=user_id,
                        pet_name=saved_profile.get("name", "不明"),
                        pet_type=saved_profile.get("pet_type", "不明"),
                        story_mode=story_mode,
                        genre=genre if story_mode == "絵本小説風（客観的な視点から）" else "おしゃべり風",
                        duration_ms=duration_ms,
                        status="ERROR",
                        error_msg=prompt_res
                    )
            finally:
                if 'loading_placeholder' in locals():
                    loading_placeholder.empty()
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                p_bar.empty()
                p_text.empty()

with col2:
    st.markdown("### 📚 完成した思い出絵本")
    if 'line_status' in st.session_state: st.info(st.session_state['line_status'])
        
    if 'display_feelings' in st.session_state and 'display_story' in st.session_state:
        feelings_text = st.session_state['display_feelings']
        story_text = st.session_state['display_story']
        manga_prompt_text = st.session_state['display_prompt']
        
        # まずアップロードした元画像を表示
        if 'display_image' in st.session_state:
            st.markdown("#### 📸 アップロードした思い出写真")
            st.image(st.session_state['display_image'], use_container_width=True)
            
        st.write("---")
        # 1. 写真の分析(ペットの気持ち分析)
        st.markdown("#### 🐶 写真の分析（ペットの気持ち分析）")
        st.markdown(f'<div class="line-preview-box">{feelings_text}</div>', unsafe_allow_html=True)
        st.write("---")
        
        # 2. ストーリー
        st.markdown("#### 📖 ストーリー")
        st.markdown(f'<div class="line-preview-box">{story_text}</div>', unsafe_allow_html=True)
        st.write("---")

        # 3. GPTが4コマ漫画を最高品質で生成する最高のプロンプト
        st.markdown("#### 🎨 GPTが4コマ漫画を最高品質で生成する最高のプロンプト")
        st.info("💡 下のプロンプトをワンクリックでコピーし、すぐ下の「ChatGPTで4コマ漫画生成」ボタンを押してChatGPTに貼り付けてください！")
        
        # --- スマホでもPCでも確実にコピー動作する、プロンプトテキスト＆コピペボタン併設の特別HTMLウィジェット ---
        html_copy_code = f"""
        <div style="display: flex; flex-direction: column; gap: 10px; width: 100%; height: 100%; box-sizing: border-box; font-family: sans-serif;">
            <textarea id="promptText" style="width: 100%; height: 190px; background-color: #1A202C; color: #FFFFFF; border: 1px solid #4A5568; border-radius: 8px; padding: 10px; font-family: monospace; font-size: 14px; box-sizing: border-box; resize: none;" readonly>{manga_prompt_text}</textarea>
            <button onclick="copyToClipboard()" style="background: linear-gradient(135deg, #FF7B93 0%, #FFB88C 100%); color: white; border: none; border-radius: 8px; padding: 12px; font-weight: bold; cursor: pointer; font-size: 15px; width: 100%; transition: opacity 0.2s;">📋 プロンプトをコピーする</button>
        </div>
        <script>
        function copyToClipboard() {{
            var copyText = document.getElementById("promptText");
            copyText.select();
            copyText.setSelectionRange(0, 99999); /* For mobile devices */
            try {{
                var successful = document.execCommand('copy');
                if (successful) {{
                    alert("プロンプトをクリップボードにコピーしました！");
                }} else {{
                    alert("コピーに失敗しました。手動でコピーしてください。");
                }}
            }} catch (err) {{
                alert("コピー機能がサポートされていません。手動でコピーしてください。");
            }}
        }}
        </script>
        """
        components.html(html_copy_code, height=255)
        
        # --- ChatGPTへ直行するボタンを設置 ---
        st.write("")
        st.link_button("🚀 ChatGPTで4コマ漫画生成", "https://chatgpt.com/", use_container_width=True)
        
    else:
        st.info("左側で写真をセットし、ボタンを押すと進捗バーが走り出し、完了後にここに心情分析と小説、そして4コマ漫画プロンプトが生成されます。")

st.write("---")
st.caption("With Love and Warmth — Powered by Gemini 2.5 Flash & NanoBanana (Imagen 3) Architecture")
