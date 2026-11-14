"""
每個來源的速率限制（記憶體內計數，單一行程有效，重啟後歸零）
"""
import time
from collections import deque

from fastapi import HTTPException, Request

# 同時追蹤的 (端點, 來源) 上限，超過就先清掉已過期的
_MAX_KEYS = 10000
_hits: dict[tuple[str, str], tuple[int, deque]] = {}


def client_ip(request: Request) -> str:
    """來源位址：X-Forwarded-For 最後一段是前面代理實際看到的連線位址，前面幾段用戶端可以自己填，不採用"""
    parts = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    if parts:
        return parts[-1]
    return request.client.host if request.client else "unknown"


def _purge(now: float) -> None:
    for key in [k for k, (window, q) in _hits.items() if not q or now - q[-1] >= window]:
        del _hits[key]
    if len(_hits) >= _MAX_KEYS:
        _hits.clear()


def rate_limit(name: str, limit: int, window_seconds: int):
    """FastAPI 相依：同一來源在 window_seconds 內最多 limit 次，超過回 429"""

    def dependency(request: Request) -> None:
        now = time.monotonic()
        key = (name, client_ip(request))
        if key not in _hits and len(_hits) >= _MAX_KEYS:
            _purge(now)
        _, q = _hits.setdefault(key, (window_seconds, deque()))
        while q and now - q[0] >= window_seconds:
            q.popleft()
        if len(q) >= limit:
            raise HTTPException(status_code=429, detail="請求太頻繁，請稍後再試")
        q.append(now)

    return dependency
