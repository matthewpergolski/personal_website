"""
Rate limiting utilities (file-backed, best-effort).

Note: On Vercel serverless this is per-instance only and will reset
on cold starts / scaling. See DEPLOYING.md for details.
"""

import json
import os
import time

from src.config import BASE_DATA_DIR  # type: ignore[attr-defined]


def _safe_filename(value: str) -> str:
    """Make a string safe to use in filenames (IPv6 etc.)."""
    if not value:
        return "unknown"
    safe = value.replace(":", "-").replace("/", "_").replace("\\", "_")
    safe = "".join(c for c in safe if c.isalnum() or c in ("-", "_", "."))
    return safe[:80] or "unknown"


def is_rate_limited(ip: str) -> bool:
    """Best-effort per-IP and global rate limiting.

    Returns True if the IP (or global limit) has been exceeded.
    """
    try:
        limit_ip = int(os.getenv("RATE_IP_PER_HOUR", "3"))
        limit_global = int(os.getenv("RATE_GLOBAL_PER_DAY", "50"))
    except Exception:
        limit_ip, limit_global = 3, 50

    now = int(time.time())
    rl_dir = BASE_DATA_DIR / "ratelimit"
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
