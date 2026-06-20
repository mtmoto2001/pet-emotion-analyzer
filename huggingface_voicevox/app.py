"""
VOICEVOX Engine FastAPI Proxy

VOICEVOXエンジンへのプロキシサーバー。
認証・レート制限・CORSを提供する。
"""

import os
import time
from typing import Optional

import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VOICEVOX_URL: str = "http://127.0.0.1:50021"
API_KEY: Optional[str] = os.environ.get("API_KEY")
RATE_LIMIT_MAX_REQUESTS: int = 10
RATE_LIMIT_WINDOW_SECONDS: int = 60

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="VOICEVOX Engine API Proxy",
    description="VOICEVOX音声合成エンジンへのプロキシAPI（認証・レート制限付き）",
    version="1.0.0",
)

# CORS — すべてのオリジンを許可（Expoアプリ対応）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Rate Limiter (in-memory, per-IP)
# ---------------------------------------------------------------------------

# { ip_address: [timestamp, ...] }
_rate_limit_store: dict[str, list[float]] = {}


def _check_rate_limit(client_ip: str) -> None:
    """IPごとのレート制限をチェックする。超過時は 429 を送出。"""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    # 古いエントリを除去
    timestamps = _rate_limit_store.get(client_ip, [])
    timestamps = [t for t in timestamps if t > window_start]
    _rate_limit_store[client_ip] = timestamps

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW_SECONDS}s.",
        )

    timestamps.append(now)


# ---------------------------------------------------------------------------
# Auth Dependency
# ---------------------------------------------------------------------------


async def verify_api_key(request: Request) -> None:
    """X-API-Key ヘッダーを検証する。API_KEY 未設定時は認証をスキップ。"""
    if API_KEY is None:
        # 開発時: API_KEY 未設定なら認証なしで通す
        return

    provided_key = request.headers.get("X-API-Key")
    if provided_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ---------------------------------------------------------------------------
# Middleware — Rate Limit (applied to all except /health, /docs, /openapi.json)
# ---------------------------------------------------------------------------

_RATE_LIMIT_EXEMPT_PATHS: set[str] = {"/health", "/docs", "/openapi.json", "/redoc"}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """レート制限ミドルウェア。除外パス以外に適用。"""
    if request.url.path not in _RATE_LIMIT_EXEMPT_PATHS:
        client_ip: str = request.client.host if request.client else "unknown"
        try:
            _check_rate_limit(client_ip)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
    response = await call_next(request)
    return response


# ---------------------------------------------------------------------------
# HTTP Client
# ---------------------------------------------------------------------------


def _get_http_client() -> httpx.AsyncClient:
    """VOICEVOXエンジンとの通信用 httpx クライアントを生成する。"""
    return httpx.AsyncClient(base_url=VOICEVOX_URL, timeout=120.0)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
async def health_check() -> dict:
    """
    ヘルスチェックエンドポイント（認証不要）。

    VOICEVOXエンジンの /version も確認して返す。
    """
    try:
        async with _get_http_client() as client:
            resp = await client.get("/version")
            voicevox_version = resp.text.strip().strip('"')
            return {
                "status": "ok",
                "voicevox_version": voicevox_version,
            }
    except Exception as e:
        return {
            "status": "degraded",
            "voicevox_version": None,
            "error": str(e),
        }


@app.post("/audio_query", dependencies=[Depends(verify_api_key)])
async def audio_query(request: Request) -> JSONResponse:
    """
    VOICEVOXの /audio_query にプロキシする。

    クエリパラメータ（text, speaker 等）をそのまま転送する。
    """
    query_string = str(request.url.query)
    body = await request.body()

    async with _get_http_client() as client:
        resp = await client.post(
            f"/audio_query?{query_string}",
            content=body,
            headers={"Content-Type": request.headers.get("Content-Type", "application/json")},
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return JSONResponse(content=resp.json(), status_code=resp.status_code)


@app.post("/synthesis", dependencies=[Depends(verify_api_key)])
async def synthesis(request: Request) -> Response:
    """
    VOICEVOXの /synthesis にプロキシする。

    クエリパラメータ（speaker 等）とリクエストボディをそのまま転送する。
    レスポンスは WAV バイナリ。
    """
    query_string = str(request.url.query)
    body = await request.body()

    async with _get_http_client() as client:
        resp = await client.post(
            f"/synthesis?{query_string}",
            content=body,
            headers={"Content-Type": request.headers.get("Content-Type", "application/json")},
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return Response(
        content=resp.content,
        media_type="audio/wav",
        status_code=resp.status_code,
    )


@app.get("/speakers", dependencies=[Depends(verify_api_key)])
async def speakers() -> JSONResponse:
    """
    VOICEVOXの /speakers にプロキシする。

    利用可能なキャラクター（話者）の一覧を返す。
    """
    async with _get_http_client() as client:
        resp = await client.get("/speakers")

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return JSONResponse(content=resp.json(), status_code=resp.status_code)
