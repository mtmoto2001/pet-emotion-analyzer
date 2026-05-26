from flask import Flask, request, jsonify
from flask_cors import CORS
import data_manager
import os

app = Flask(__name__)
# すべてのオリジンからのCORS（クロスオリジン要求）を許可し、モバイルアプリ（Expo Go）からの接続を保証します
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/api/key", methods=["GET"])
def get_api_key():
    """
    管理者（このMac）に登録されているGoogle Gemini APIキーをクライアントアプリに返します。
    """
    config = data_manager.load_config()
    key = config.get("GOOGLE_API_KEY", "")
    if not key:
        return jsonify({"error": "Gemini API key is not registered on admin PC"}), 404
    return jsonify({"GOOGLE_API_KEY": key})

@app.route("/api/log", methods=["POST"])
def log_usage():
    """
    参加者のスマホアプリからストーリー生成時のログを受け取り、Macの usage_log.jsonl に追記します。
    """
    data = request.json or {}
    user_id = data.get("user_id", "unknown")
    pet_name = data.get("pet_name", "不明")
    pet_type = data.get("pet_type", "不明")
    story_mode = data.get("story_mode", "不明")
    genre = data.get("genre", "不明")
    duration_ms = data.get("duration_ms", 0)
    status = data.get("status", "SUCCESS")
    error_msg = data.get("error_msg", "")
    
    # data_manager のログ機能を利用して書き込み
    data_manager.log_usage(
        user_id=user_id,
        pet_name=pet_name,
        pet_type=pet_type,
        story_mode=story_mode,
        genre=genre,
        duration_ms=duration_ms,
        status=status,
        error_msg=error_msg
    )
    return jsonify({"status": "logged"})

@app.route("/api/profile", methods=["POST"])
def save_profile():
    """
    参加者のスマホアプリから登録されたペットプロファイルを受け取り、Macに保存します。
    これで管理画面の「世帯一覧」に即時リアルタイム反映されます。
    """
    data = request.json or {}
    user_id = data.get("user_id")
    profile_data = data.get("profile")
    
    if not user_id or not profile_data:
        return jsonify({"error": "Missing user_id or profile data"}), 400
        
    data_manager.save_profile(profile_data, user_id=user_id)
    return jsonify({"status": "saved"})

@app.route("/api/profile/<user_id>", methods=["GET"])
def get_profile(user_id):
    """
    暗証番号などでログイン（データ復元）した際、Macの保存ファイルからプロファイルデータを引き出しクライアントへ返します。
    """
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
        
    profile = data_manager.load_profile(user_id=user_id)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
        
    return jsonify(profile)

if __name__ == "__main__":
    # ポート 8082 で起動し、外部（同じWi-Fi内のスマホ等）からのアクセスを受け入れます
    app.run(host="0.0.0.0", port=8082, debug=False)
