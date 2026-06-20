---
title: VOICEVOX Engine API
emoji: 🎙️
colorFrom: pink
colorTo: red
sdk: docker
app_port: 7860
---

# VOICEVOX Engine API

VOICEVOX音声合成エンジンのクラウドAPI。認証キー必須。

## エンドポイント

| パス | メソッド | 説明 |
|------|----------|------|
| `/health` | GET | ヘルスチェック（認証不要） |
| `/speakers` | GET | 話者一覧の取得 |
| `/audio_query` | POST | 音声合成用クエリの作成 |
| `/synthesis` | POST | 音声合成（WAV形式） |

## 認証

すべてのリクエスト（`/health` を除く）に `X-API-Key` ヘッダーが必要です。
API キーは Hugging Face Spaces の Secrets で `API_KEY` として設定してください。
