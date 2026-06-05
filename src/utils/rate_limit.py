"""
Rate limiting utilities (file-backed, best-effort).

Note: On Vercel serverless this is per-instance only and will reset
on cold starts / scaling. See DEPLOYING.md for details.
"""

import json
import os
import time
from dataclasses import dataclass

from src.config import BASE_DATA_DIR  # type: ignore[attr-defined]


@dataclass(frozen=True)
class RateLimitConfig:
    scope: str
    ip_env: str
    global_env: str
    default_ip_per_hour: int
    default_global_per_day: int


def _safe_filename(value: str) -> str:
    """Make a string safe to use in filenames (IPv6 etc.)."""
    if not value:
        return "unknown"
    safe = value.replace(":", "-").replace("/", "_").replace("\\", "_")
    safe = "".join(c for c in safe if c.isalnum() or c in ("-", "_", "."))
    return safe[:80] or "unknown"


CONTACT_RATE_LIMIT = RateLimitConfig(
    scope="contact",
    ip_env="RATE_IP_PER_HOUR",
    global_env="RATE_GLOBAL_PER_DAY",
    default_ip_per_hour=3,
    default_global_per_day=50,
)

CHAT_RATE_LIMIT = RateLimitConfig(
    scope="chat",
    ip_env="RATE_CHAT_IP_PER_HOUR",
    global_env="RATE_CHAT_GLOBAL_PER_DAY",
    default_ip_per_hour=30,
    default_global_per_day=500,
)


def is_rate_limited(ip: str, config: RateLimitConfig = CONTACT_RATE_LIMIT) -> bool:
    """Best-effort per-IP and global rate limiting.

    Returns True if the IP (or global limit) has been exceeded.
    """
    try:
        limit_ip = int(os.getenv(config.ip_env, str(config.default_ip_per_hour)))
        limit_global = int(
            os.getenv(config.global_env, str(config.default_global_per_day))
        )
    except Exception:
        limit_ip, limit_global = (
            config.default_ip_per_hour,
            config.default_global_per_day,
        )

    now = int(time.time())
    rl_dir = BASE_DATA_DIR / "ratelimit" / config.scope
    try:
        rl_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    safe_ip = _safe_filename(ip)
    ipf = rl_dir / f"{safe_ip}.json"

    try:
        lst = json.loads(ipf.read_text())
    except Exception:
        lst = []

    lst = [t for t in lst if now - int(t) < 3600]
    if len(lst) >= limit_ip:
        try:
            ipf.write_text(json.dumps(lst))
        except Exception:
            pass
        return True

    lst.append(now)
    try:
        ipf.write_text(json.dumps(lst))
    except Exception:
        pass

    gf = rl_dir / "global.json"
    try:
        gl = json.loads(gf.read_text())
    except Exception:
        gl = []

    gl = [t for t in gl if now - int(t) < 86400]
    if len(gl) >= limit_global:
        try:
            gf.write_text(json.dumps(gl))
        except Exception:
            pass
        return True

    gl.append(now)
    try:
        gf.write_text(json.dumps(gl))
    except Exception:
        pass
    return False
