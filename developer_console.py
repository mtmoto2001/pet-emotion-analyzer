import streamlit as st
import pandas as pd
import json
import os
import datetime
import data_manager
import ai_core
import line_api

# 繝壹�繧ｸ讒区�險ｭ螳�
st.set_page_config(page_title="Pet Daily AI - 髢狗匱閠�さ繝ｳ繝医Ο繝ｼ繝ｫ繧ｻ繝ｳ繧ｿ繝ｼ", page_icon="�屏��", layout="wide")

# 繧ｫ繧ｹ繧ｿ繝�CSS縺ｧ髢狗匱閠�判髱｢繧峨＠縺�す繝｣繝ｼ繝励〒繝｢繝繝ｳ縺ｪ繝�じ繧､繝ｳ縺ｸ
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Noto+Sans+JP:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Noto Sans JP', sans-serif;
    }
    .console-header {
        background: linear-gradient(135deg, #1E1E2F 0%, #2A2A40 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid #3A3A55;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    .console-title {
        color: #00E6FF;
        font-weight: 700;
        font-size: 2.2rem;
        margin: 0;
    }
    .console-subtitle {
        color: #A0A0C0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    .kpi-card {
        background-color: #1E1E2E;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #00E6FF;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        text-align: center;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.2rem;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #A0A0C0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .code-font {
        font-family: 'Fira Code', monospace;
    }
</style>
""", unsafe_allow_html=True)

# 髢狗匱閠�さ繝ｳ繧ｽ繝ｼ繝ｫ繧ｿ繧､繝医Ν繝倥ャ繝繝ｼ
st.markdown("""
<div class="console-header">
    <h1 class="console-title">�誓 Pet Daily AI Developer Console</h1>
    <p class="console-subtitle">螳溯ｨｼPoC 10荳門ｸｯ蜷代￠繧ｷ繧ｹ繝�Β逶｣隕悶�繝�Ξ繝｡繝医Μ繝ｻAPI逍朱夂｢ｺ隱阪さ繝ｳ繝医Ο繝ｼ繝ｫ繧ｻ繝ｳ繧ｿ繝ｼ</p>
</div>
""", unsafe_allow_html=True)

# 險ｭ螳壹ョ繝ｼ繧ｿ縺ｮ繝ｭ繝ｼ繝�
config = data_manager.load_config()

# 髢狗匱閠�さ繝ｳ繧ｽ繝ｼ繝ｫ縺ｮ繧ｵ繧､繝峨ヰ繝ｼ險ｭ螳夲ｼ医け繝ｩ繧ｦ繝峨ョ繝ｼ繧ｿ蜷梧悄繝医げ繝ｫ��
st.sidebar.markdown("### 笘�ｸ� 繧ｯ繝ｩ繧ｦ繝蛾｣謳ｺ險ｭ螳�")
data_source = st.sidebar.radio(
    "繝��繧ｿ繧ｽ繝ｼ繧ｹ蛻�ｊ譖ｿ縺�", 
    ["�刀 繝ｭ繝ｼ繧ｫ繝ｫ繝輔ぃ繧､繝ｫ陦ｨ遉ｺ", "笘�ｸ� 繧ｯ繝ｩ繧ｦ繝会ｼ�oogle Sheets�牙酔譛�"], 
    index=1,
    help="繧ｹ繝槭�螳滓ｩ溘°繧烏oogle Sheets縺ｫ騾∽ｿ｡縺輔ｌ縺溷�荳門ｸｯ繝��繧ｿ縺ｨ螳溯｡後Ο繧ｰ繧偵Μ繧｢繝ｫ繧ｿ繧､繝�縺ｧ蜷梧悄縺励∪縺吶�"
)

# 繝�ヵ繧ｩ繝ｫ繝医�GAS繝励Ο繧ｭ繧ｷURL
default_proxy_url = "https://script.google.com/macros/s/AKfycby_yneEPDfmGGpGrZwCgEWt3KIQxZ_5V5LgX_8z9ItloS_Pg0p-SxsAqBW0OFdWa_WFog/exec"

# 繝ｭ繧ｰ繝輔ぃ繧､繝ｫ縺ｮ險ｭ螳�
log_file = data_manager.USAGE_LOG_FILE
logs = []
profiles = []

if data_source == "笘�ｸ� 繧ｯ繝ｩ繧ｦ繝会ｼ�oogle Sheets�牙酔譛�":
    api_key = config.get("GOOGLE_API_KEY", "")
    with st.spinner("繧ｯ繝ｩ繧ｦ繝我ｸ翫� Google Sheets 繝��繧ｿ繝吶�繧ｹ蜷梧悄荳ｭ..."):
        logs = data_manager.load_logs_cloud(default_proxy_url, api_key)
        profiles = data_manager.load_all_profiles() # 蠢ｵ縺ｮ縺溘ａ繝ｭ繝ｼ繧ｫ繝ｫ蛛ｴ繧ゅヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ逕ｨ縺ｫ蜿門ｾ�
        cloud_profiles = data_manager.load_profiles_cloud(default_proxy_url, api_key)
        if cloud_profiles:
            profiles = cloud_profiles
else:
    # 繝ｭ繝ｼ繧ｫ繝ｫ繝輔ぃ繧､繝ｫ縺ｮ隱ｭ縺ｿ霎ｼ縺ｿ
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.strip():
                        try:
                            logs.append(json.loads(line.strip()))
                        except:
                            pass
        except Exception as e:
            st.error(f"ログファイルの読み込みエラー: {e}")
    profiles = data_manager.load_all_profiles()

df_logs = pd.DataFrame(logs)
df_profiles = pd.DataFrame(profiles)

# --- 1. KPI繝繝�す繝･繝懊�繝峨お繝ｪ繧｢ ---
st.markdown("### �投 繧ｷ繧ｹ繝�Β蛻ｩ逕ｨ迥ｶ豕√し繝槭Μ繝ｼ")
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

total_households = len(df_profiles) if not df_profiles.empty else 0
total_generations = len(df_logs) if not df_logs.empty else 0
error_count = len(df_logs[df_logs["status"] == "ERROR"]) if not df_logs.empty and "status" in df_logs.columns else 0
error_rate = (error_count / total_generations * 100) if total_generations > 0 else 0.0

with col_kpi1:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #00E6FF;">
        <div class="kpi-value">{total_households}</div>
        <div class="kpi-label">逋ｻ骭ｲ荳ｭ縺ｮ荳門ｸｯ謨ｰ (繧ｹ繝槭�)</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #FFB800;">
        <div class="kpi-value">{total_generations}</div>
        <div class="kpi-label">邏ｯ險医せ繝医�繝ｪ繝ｼ逕滓�蝗樊焚</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #FF4A4A;">
        <div class="kpi-value">{error_count}</div>
        <div class="kpi-label">繧ｷ繧ｹ繝�Β繧ｨ繝ｩ繝ｼ逋ｺ逕滓焚</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #A652FF;">
        <div class="kpi-value">{error_rate:.1f}%</div>
        <div class="kpi-label">API繧ｨ繝ｩ繝ｼ逋ｺ逕溽紫</div>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# 繝｡繧､繝ｳ繧ｿ繝匁ｧ区�
tab_dashboard, tab_households, tab_api_test, tab_raw_logs = st.tabs([
    "�嶋 蛻ｩ逕ｨ繧ｰ繝ｩ繝募�譫�", 
    "�升 逋ｻ骭ｲ荳門ｸｯ荳隕ｧ", 
    "�泊 API逍朱壹ユ繧ｹ繝茨ｼ�ｮ｡逅�", 
    "�統 繧ｵ繝ｼ繝舌�逕溘Ο繧ｰ繝薙Η繝ｼ繝ｯ繝ｼ"
])

# --- TAB 1: 繧ｰ繝ｩ繝募�譫� ---
with tab_dashboard:
    if df_logs.empty:
        st.info("繝��繧ｿ縺後≠繧翫∪縺帙ｓ縲よ昴＞蜃ｺ繧ｹ繝医�繝ｪ繝ｼ縺檎函謌舌＆繧後ｋ縺ｨ縲√％縺薙↓繧ｰ繝ｩ繝募�譫舌′繝ｪ繧｢繝ｫ繧ｿ繧､繝�謠冗判縺輔ｌ縺ｾ縺咀汾ｾ")
    else:
        g_col1, g_col2 = st.columns(2)
        
        with g_col1:
            st.markdown("#### �生 荳門ｸｯ�医�繝�ヨ蜷搾ｼ牙挨縺ｮ諤昴＞蜃ｺ逕滓�鬆ｻ蠎ｦ")
            # user_id 縺ｨ pet_name 縺ｮ邨�∩蜷医ｏ縺帙〒繧ｫ繧ｦ繝ｳ繝�
            if "pet_name" in df_logs.columns:
                active_users = df_logs.groupby(["user_id", "pet_name"]).size().reset_index(name="逕滓�蝗樊焚")
                active_users["陦ｨ遉ｺ蜷�"] = active_users["pet_name"] + " (" + active_users["user_id"] + ")"
                active_users = active_users.sort_values(by="逕滓�蝗樊焚", ascending=False)
                st.bar_chart(active_users.set_index("陦ｨ遉ｺ蜷�")["逕滓�蝗樊焚"], horizontal=True, color="#00E6FF")
            
        with g_col2:
            st.markdown("#### �答 莠ｺ豌励�蟆剰ｪｬ繧ｸ繝｣繝ｳ繝ｫ蜑ｲ蜷�")
            if "genre" in df_logs.columns:
                # 縺ｻ縺ｮ縺ｼ縺ｮ譌･蟶ｸ鬚ｨ縲∵°諢帛ｰ剰ｪｬ鬚ｨ縺ｪ縺ｩ縺ｮ蜃ｺ迴ｾ蝗樊焚繧帝寔險�
                genre_counts = df_logs[df_logs["genre"] != ""]["genre"].value_counts()
                st.bar_chart(genre_counts, color="#FFB800")
        
        st.write("")
        st.markdown("#### 竢ｳ 譎る俣蟶ｯ蛻･繧ｹ繝医�繝ｪ繝ｼ逕滓�繧｢繧ｯ繝�ぅ繝薙ユ繧｣")
        if "timestamp" in df_logs.columns:
            # 繧ｿ繧､繝�繧ｹ繧ｿ繝ｳ繝励ｒ譎る俣蜊倅ｽ搾ｼ�YYY-MM-DD HH�峨〒髮�ｨ�
            try:
                df_logs["date_hour"] = pd.to_datetime(df_logs["timestamp"]).dt.strftime("%Y-%m-%d %H:00")
                hourly_counts = df_logs.groupby("date_hour").size().reset_index(name="逕滓�蝗樊焚")
                st.line_chart(hourly_counts.set_index("date_hour")["逕滓�蝗樊焚"], color="#A652FF")
            except Exception as e:
                st.caption(f"譎らｳｻ蛻励ヱ繝ｼ繧ｹ繧ｨ繝ｩ繝ｼ: {e}")

# --- TAB 2: 逋ｻ骭ｲ荳門ｸｯ荳隕ｧ ---
with tab_households:
    st.markdown("#### �升 逋ｻ骭ｲ荳門ｸｯ��10荳門ｸｯPoC�峨�繝壹ャ繝医�繝ｭ繝輔ぅ繝ｼ繝ｫ荳隕ｧ")
    st.write("荳闊ｬ繝ｦ繝ｼ繧ｶ繝ｼ縺後せ繝槭�繝医ヵ繧ｩ繝ｳ縺九ｉ蛻晏屓逋ｻ骭ｲ繝ｻ譖ｴ譁ｰ縺励◆繝壹ャ繝域ュ蝣ｱ縺御ｸ隕ｧ縺ｧ遒ｺ隱阪〒縺阪∪縺呻ｼ域怙譁ｰ鬆�ｼ峨�")
    
    if df_profiles.empty:
        st.warning("縺ｾ縺�逋ｻ骭ｲ荳門ｸｯ縺後≠繧翫∪縺帙ｓ縲ゅΘ繝ｼ繧ｶ繝ｼ縺後せ繝槭�縺ｧ逋ｻ骭ｲ縺吶ｋ縺ｨ縲√％縺薙↓閾ｪ蜍戊｡ｨ遉ｺ縺輔ｌ縺ｾ縺吶�")
    else:
        # 陦ｨ遉ｺ逕ｨ縺ｫ�    st.markdown("##### �東 迴ｾ蝨ｨ繝ｭ繝ｼ繝峨＆繧後※縺�ｋ雉��ｼ諠��ｱ")
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        st.markdown(f"**Gemini API繧ｭ繝ｼ:** <span class='code-font'>{mask_key(config.get('GOOGLE_API_KEY'))}</span>", unsafe_allow_html=True)
    with col_c2:
        st.markdown(f"**LINE繝医�繧ｯ繝ｳ:** <span class='code-font'>{mask_key(config.get('LINE_CHANNEL_ACCESS_TOKEN'))}</span>", unsafe_allow_html=True)
    with col_c3:
        st.markdown(f"**VOICEVOX URL:** <span class='code-font'>{config.get('VOICEVOX_API_URL', '譛ｪ險ｭ螳� �閥')}</span>", unsafe_allow_html=True)
    with col_c4:
        st.markdown(f"**VOICEVOX API繧ｭ繝ｼ:** <span class='code-font'>{mask_key(config.get('VOICEVOX_API_KEY'))}</span>", unsafe_allow_html=True)
    
    st.write("---")
    
    # 逍朱壹ユ繧ｹ繝医ヵ繧ｩ繝ｼ繝�
    st.markdown("##### 笞｡ API謗･邯夂鮪騾壹ユ繧ｹ繝�")
    st.write("縲後ユ繧ｹ繝亥ｮ溯｡後阪�繧ｿ繝ｳ繧呈款縺吶→縲∝ｮ滄圀縺ｮAPI縺ｫ蟇ｾ縺励※雜�ｻｽ驥上↑繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ騾√ｊ縲√く繝ｼ縺梧悽蠖薙↓譛牙柑縺ｧ郢九′縺｣縺ｦ縺�ｋ縺九ｒ讀懆ｨｼ縺ｧ縺阪∪縺吶�")
    
    test_google, test_line = st.columns(2)
    
    with test_google:
        st.markdown("###### �､� Gemini API 謗･邯壹ユ繧ｹ繝�")
        st.caption("Gemini 2.5 Flash 縺ｫ縲後％繧薙↓縺｡縺ｯ�誓縲阪→騾∽ｿ｡縺励�1蜊倩ｪ槭�蠢懃ｭ斐ｒ蠕�■縺ｾ縺吶�")
        if st.button("�伯 Gemini API 逍朱壹ユ繧ｹ繝医ｒ螳溯｡�", key="btn_test_gemini", use_container_width=True):
            api_key = config.get("GOOGLE_API_KEY")
            if not api_key:
                st.error("Gemini API繧ｭ繝ｼ縺梧悴險ｭ螳壹〒縺吶�")
            else:
                with st.spinner("謗･邯壽､懆ｨｼ荳ｭ..."):
                    try:
                        # 雜�ｻｽ驥上Μ繧ｯ繧ｨ繧ｹ繝�
                        response = ai_core.run_lightweight_test(api_key)
                        st.success("�泙 Gemini API 謗･邯夂鮪騾壹↓謌仙粥縺励∪縺励◆��")
                        st.info(f"AI縺九ｉ縺ｮ蠢懃ｭ�: {response}")
                    except Exception as e:
                        st.error(f"�閥 謗･邯壼､ｱ謨�: {e}")
                        
    with test_line:
        st.markdown("###### �町 LINE Messaging API 繝�せ繝�")
        st.caption("LINE繝√Ε繝ｳ繝阪Ν繧｢繧ｯ繧ｻ繧ｹ繝医�繧ｯ繝ｳ繧堤畑縺�※縲√ム繝溘�縺ｮ繝悶Ο繝ｼ繝峨く繝｣繧ｹ繝磯∽ｿ｡縺窟PI繝ｬ繝吶Ν縺ｧ蜿励￠蜈･繧後ｉ繧後ｋ縺区､懆ｨｼ縺励∪縺吶�")
        if st.button("�伯 LINE API 逍朱壹ユ繧ｹ繝医ｒ螳溯｡�", key="btn_test_line", use_container_width=True):
            line_token = config.get("LINE_CHANNEL_ACCESS_TOKEN")
            if not line_token:
                st.error("LINE繧｢繧ｯ繧ｻ繧ｹ繝医�繧ｯ繝ｳ縺梧悴險ｭ螳壹〒縺吶�")
            else:
                with st.spinner("LINE逍朱壽､懆ｨｼ荳ｭ..."):
                    # LINE縺ｮ逍朱夂｢ｺ隱� (繝繝溘�繝｡繝�そ繝ｼ繧ｸ縺梧拠蜷ｦ縺輔ｌ縺ｪ縺�°遒ｺ隱�)
                    status = line_api.test_line_credentials(line_token)
                    if "謌仙粥" in status or "200" in status or "400" in status:
                        # 400繧ｨ繝ｩ繝ｼ(辟｡蜉ｹ縺ｪ繝｡繝�そ繝ｼ繧ｸ遲�)縺ｧ繧りｪ崎ｨｼ閾ｪ菴薙�騾壹▲縺ｦ縺�ｌ縺ｰ逍朱壽�蜉溘→縺ｿ縺ｪ縺�
                        st.success("�泙 LINE API 繧ｨ繝ｳ繝峨�繧､繝ｳ繝医→縺ｮ逍朱壹ｒ遒ｺ隱阪＠縺ｾ縺励◆��")
                        st.info(f"API蠢懃ｭ斐せ繝��繧ｿ繧ｹ: {status}")
                    else:
                        st.error(f"�閥 LINE逍朱壼､ｱ謨�: {status}")
                        
    st.write("---")
    
    # 繧ｭ繝ｼ險ｭ螳壻ｸ頑嶌縺堺ｿ晏ｭ倥ヵ繧ｩ繝ｼ繝�
    st.markdown("##### �統 繝ｭ繝ｼ繧ｫ繝ｫ API險ｭ螳壹�逶ｴ謗･邱ｨ髮�")
    st.write("繝ｭ繝ｼ繧ｫ繝ｫ縺ｮ `config.json` 繧堤峩謗･邱ｨ髮�＠縺ｦ荳頑嶌縺堺ｿ晏ｭ倥＠縺ｾ縺吶よ悽逡ｪ繧ｵ繝ｼ繝舌�縺ｮ譖ｴ譁ｰ逕ｨSecrets繝医�繧ｯ繝ｳ縺ｮ謗ｧ縺医→縺励※繧ょ茜逕ｨ縺ｧ縺阪∪縺吶�")
    
    with st.form(key="form_dev_config"):
        edit_line = st.text_input("LINE繧｢繧ｯ繧ｻ繧ｹ繝医�繧ｯ繝ｳ", value=config.get("LINE_CHANNEL_ACCESS_TOKEN", ""), type="password")
        edit_google = st.text_input("Google Gemini API繧ｭ繝ｼ", value=config.get("GOOGLE_API_KEY", ""), type="password")
        edit_voicevox_url = st.text_input("VOICEVOX 謗･邯壼�URL", value=config.get("VOICEVOX_API_URL", ""))
        edit_voicevox_key = st.text_input("VOICEVOX API繧ｭ繝ｼ", value=config.get("VOICEVOX_API_KEY", ""), type="password")
        
        btn_save = st.form_submit_button("�沈 繝ｭ繝ｼ繧ｫ繝ｫ config.json 縺ｫ菫晏ｭ�")
        if btn_save:
            data_manager.save_config(edit_line, edit_google, edit_voicevox_url, edit_voicevox_key)
            st.success("繝ｭ繝ｼ繧ｫ繝ｫ config.json 繧呈峩譁ｰ縺励∪縺励◆��")
            st.rerun()
mini", use_container_width=True):
            api_key = config.get("GOOGLE_API_KEY")
            if not api_key:
                st.error("Gemini API繧ｭ繝ｼ縺梧悴險ｭ螳壹〒縺吶�")
            else:
                with st.spinner("謗･邯壽､懆ｨｼ荳ｭ..."):
                    try:
                        # 雜�ｻｽ驥上Μ繧ｯ繧ｨ繧ｹ繝�
                        response = ai_core.run_lightweight_test(api_key)
                        st.success("�泙 Gemini API 謗･邯夂鮪騾壹↓謌仙粥縺励∪縺励◆��")
                        st.info(f"AI縺九ｉ縺ｮ蠢懃ｭ�: {response}")
                    except Exception as e:
                        st.error(f"�閥 謗･邯壼､ｱ謨�: {e}")
                        
    with test_line:
        st.markdown("###### �町 LINE Messaging API 繝�せ繝�")
        st.caption("LINE繝√Ε繝ｳ繝阪Ν繧｢繧ｯ繧ｻ繧ｹ繝医�繧ｯ繝ｳ繧堤畑縺�※縲√ム繝溘�縺ｮ繝悶Ο繝ｼ繝峨く繝｣繧ｹ繝磯∽ｿ｡縺窟PI繝ｬ繝吶Ν縺ｧ蜿励￠蜈･繧後ｉ繧後ｋ縺区､懆ｨｼ縺励∪縺吶�")
        if st.button("�伯 LINE API 逍朱壹ユ繧ｹ繝医ｒ螳溯｡�", key="btn_test_line", use_container_width=True):
            line_token = config.get("LINE_CHANNEL_ACCESS_TOKEN")
            if not line_token:
                st.error("LINE繧｢繧ｯ繧ｻ繧ｹ繝医�繧ｯ繝ｳ縺梧悴險ｭ螳壹〒縺吶�")
            else:
                with st.spinner("LINE逍朱壽､懆ｨｼ荳ｭ..."):
                    # LINE縺ｮ逍朱夂｢ｺ隱� (繝繝溘�繝｡繝�そ繝ｼ繧ｸ縺梧拠蜷ｦ縺輔ｌ縺ｪ縺�°遒ｺ隱�)
                    status = line_api.test_line_credentials(line_token)
                    if "謌仙粥" in status or "200" in status or "400" in status:
                        # 400繧ｨ繝ｩ繝ｼ(辟｡蜉ｹ縺ｪ繝｡繝�そ繝ｼ繧ｸ遲�)縺ｧ繧りｪ崎ｨｼ閾ｪ菴薙�騾壹▲縺ｦ縺�ｌ縺ｰ逍朱壽�蜉溘→縺ｿ縺ｪ縺�
                        st.success("�泙 LINE API 繧ｨ繝ｳ繝峨�繧､繝ｳ繝医→縺ｮ逍朱壹ｒ遒ｺ隱阪＠縺ｾ縺励◆��")
                        st.info(f"API蠢懃ｭ斐せ繝��繧ｿ繧ｹ: {status}")
                    else:
                        st.error(f"�閥 LINE逍朱壼､ｱ謨�: {status}")
                        
    st.write("---")
    
    # 繧ｭ繝ｼ險ｭ螳壻ｸ頑嶌縺堺ｿ晏ｭ倥ヵ繧ｩ繝ｼ繝�
    st.markdown("##### �統 繝ｭ繝ｼ繧ｫ繝ｫ API險ｭ螳壹�逶ｴ謗･邱ｨ髮�")
    st.write("繝ｭ繝ｼ繧ｫ繝ｫ縺ｮ `config.json` 繧堤峩謗･邱ｨ髮�＠縺ｦ荳頑嶌縺堺ｿ晏ｭ倥＠縺ｾ縺吶よ悽逡ｪ繧ｵ繝ｼ繝舌�縺ｮ譖ｴ譁ｰ逕ｨSecrets繝医�繧ｯ繝ｳ縺ｮ謗ｧ縺医→縺励※繧ょ茜逕ｨ縺ｧ縺阪∪縺吶�")
    
    with st.form(key="form_dev_config"):
        edit_line = st.text_input("LINE繧｢繧ｯ繧ｻ繧ｹ繝医�繧ｯ繝ｳ", value=config.get("LINE_CHANNEL_ACCESS_TOKEN", ""), type="password")
        edit_google = st.text_input("Google Gemini API繧ｭ繝ｼ", value=config.get("GOOGLE_API_KEY", ""), type="password")
        
        btn_save = st.form_submit_button("�沈 繝ｭ繝ｼ繧ｫ繝ｫ config.json 縺ｫ菫晏ｭ�")
        if btn_save:
            data_manager.save_config(edit_line, edit_google)
            st.success("繝ｭ繝ｼ繧ｫ繝ｫ config.json 繧呈峩譁ｰ縺励∪縺励◆��")
            st.rerun()

# --- TAB 4: 繧ｵ繝ｼ繝舌�逕溘Ο繧ｰ繝薙Η繝ｼ繝ｯ繝ｼ ---
with tab_raw_logs:
    st.markdown("#### �統 繧ｵ繝ｼ繝舌�螳溯｡後Ο繧ｰ�医ョ繝舌ャ繧ｰ��ヨ繝ｬ繝ｼ繧ｹ逕ｨ��")
    st.write("諤昴＞蜃ｺ繧ｹ繝医�繝ｪ繝ｼ逕滓�繝ｪ繧ｯ繧ｨ繧ｹ繝医＃縺ｨ縺ｮ縲∫函縺ｮ隧ｳ邏ｰ縺ｪ螳溯｡後ョ繝ｼ繧ｿ繧偵Μ繧｢繝ｫ繧ｿ繧､繝�縺ｧ譎らｳｻ蛻励〒遒ｺ隱阪〒縺阪∪縺呻ｼ域怙譁ｰ50莉ｶ�峨�")
    
    if df_logs.empty:
        st.warning("螳溯｡後Ο繧ｰ縺後∪縺�縺ゅｊ縺ｾ縺帙ｓ縲ゅい繝励Μ縺悟虚菴懊☆繧九→縺薙％縺ｫ霑ｽ險倥＆繧後∪縺吶�")
    else:
        # 譁ｰ縺励＞鬆�↓繧ｽ繝ｼ繝�
        df_logs_sorted = df_logs.iloc[::-1].head(50)
        
        # 陦ｨ遉ｺ隱ｿ謨ｴ
        st.dataframe(
            df_logs_sorted,
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.TextColumn("螳溯｡梧凾蛻ｻ", width="medium"),
                "user_id": st.column_config.TextColumn("荳門ｸｯID", width="small"),
                "pet_name": st.column_config.TextColumn("繝壹ャ繝亥錐", width="small"),
                "duration_ms": st.column_config.NumberColumn("逕滓�譎る俣 (ms)", format="%d ms"),
                "status": st.column_config.TextColumn("謌仙凄", width="small"),
                "error_msg": st.column_config.TextColumn("繧ｨ繝ｩ繝ｼ繝ｭ繧ｰ", width="large")
            }
        )
        
        # 繝ｭ繧ｰ繧ｯ繝ｪ繧｢繝懊ち繝ｳ
        st.write("---")
        st.markdown("##### 笞��� 繝ｭ繧ｰ繝輔ぃ繧､繝ｫ縺ｮ繝｡繝ｳ繝�リ繝ｳ繧ｹ")
        if data_source == "笘�ｸ� 繧ｯ繝ｩ繧ｦ繝会ｼ�oogle Sheets�牙酔譛�":
            st.info("笘�ｸ� 繧ｯ繝ｩ繧ｦ繝峨Δ繝ｼ繝峨〒縺ｯ繧ｹ繝励Ξ繝�ラ繧ｷ繝ｼ繝井ｸ翫�逕溘ョ繝ｼ繧ｿ繧堤峩謗･蜑企勁縺吶ｋ縺薙→縺ｯ縺ｧ縺阪∪縺帙ｓ縲�oogle Drive縺九ｉ縲傘etDailyAI_Database縲上ｒ髢九＞縺ｦ繝ｭ繧ｰ陦後ｒ逶ｴ謗･蜑企勁縺励※縺上□縺輔＞縲�")
        else:
            if st.button("�卵�� 螳溯｡後Ο繧ｰ繧偵☆縺ｹ縺ｦ豸亥悉縺吶ｋ", key="btn_clear_logs_dev"):
                try:
                    if os.path.exists(log_file):
                        os.remove(log_file)
                    st.success("繝ｭ繧ｰ繝輔ぃ繧､繝ｫ繧貞ｮ悟�縺ｫ豸亥悉縺励∪縺励◆縲�")
                    st.rerun()
                except Exception as e:
                    st.error(f"繝ｭ繧ｰ豸亥悉螟ｱ謨�: {e}")

st.write("---")
st.caption("Pet Daily AI Developer Console - Strictly for Local Diagnostics & Development Support")
