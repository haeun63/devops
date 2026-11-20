"""
DevOps 수업용 템플릿 애플리케이션 - 방명록(Guestbook)
"""
import os
import socket
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------
# 설정 (환경변수로 주입)
# ---------------------------------------------------------------
APP_TITLE = os.environ.get("APP_TITLE", "DevOps 방명록")
THEME_COLOR = os.environ.get("THEME_COLOR", "#DC143C")
PORT = int(os.environ.get("PORT", 5000))

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

HOSTNAME = socket.gethostname()

# ---------------------------------------------------------------
# 저장소: Redis 또는 메모리
# ---------------------------------------------------------------
redis_client = None
_memory_entries = []
_memory_visits = 0

if REDIS_HOST:
    try:
        import redis

        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=2,
        )
        redis_client.ping()
        print(f"[INFO] Redis 연결 성공: {REDIS_HOST}:{REDIS_PORT}", flush=True)
    except Exception as e:
        print(f"[WARN] Redis 연결 실패 ({e}) → 메모리 모드로 동작합니다.", flush=True)
        redis_client = None
else:
    print("[INFO] REDIS_HOST 없음 → 메모리 모드로 동작합니다.", flush=True)


def add_entry(name: str, message: str) -> None:
    item = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}|{name}|{message}"
    if redis_client:
        redis_client.lpush("guestbook:entries", item)
        redis_client.ltrim("guestbook:entries", 0, 49)   # 최근 50개만 유지
    else:
        _memory_entries.insert(0, item)
        del _memory_entries[50:]


def get_entries() -> list:
    raw = (
        redis_client.lrange("guestbook:entries", 0, 49)
        if redis_client
        else _memory_entries
    )
    result = []
    for line in raw:
        parts = line.split("|", 2)
        if len(parts) == 3:
            result.append({"time": parts[0], "name": parts[1], "message": parts[2]})
    return result


def incr_visits() -> int:
    global _memory_visits
    if redis_client:
        return redis_client.incr("guestbook:visits")
    _memory_visits += 1
    return _memory_visits


# ---------------------------------------------------------------
# 라우트
# ---------------------------------------------------------------
@app.route("/")
def index():
    visits = incr_visits()
    return render_template(
        "index.html",
        title=APP_TITLE,
        color=THEME_COLOR,
        hostname=HOSTNAME,
        visits=visits,
        entries=get_entries(),
        storage="Redis" if redis_client else "Memory",
    )


@app.route("/add", methods=["POST"])
def add():
    name = (request.form.get("name") or "익명").strip()[:20]
    message = (request.form.get("message") or "").strip()[:200]
    if message:
        add_entry(name, message)
    return redirect(url_for("index"))


@app.route("/api/entries")
def api_entries():
    """JSON API"""
    return jsonify({"count": len(get_entries()), "entries": get_entries()})


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "hostname": HOSTNAME}), 200


@app.route("/readyz")
def readyz():
    if REDIS_HOST and not redis_client:
        return jsonify({"status": "not ready", "reason": "redis unavailable"}), 503
    if redis_client:
        try:
            redis_client.ping()
        except Exception:
            return jsonify({"status": "not ready", "reason": "redis ping failed"}), 503
    return jsonify({"status": "ready"}), 200


if __name__ == "__main__":
    print(f"[INFO] {APP_TITLE} 시작 — http://0.0.0.0:{PORT}", flush=True)
    app.run(host="0.0.0.0", port=PORT)
# 테스트
