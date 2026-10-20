"""验收脚本:限流 429 测试 —— 不烧钱测法:手动把 Redis 计数顶到临界值,一发即炸

运行方式:在【项目根目录】执行
    python test_rate_limit.py
前提:uvicorn 已启动(8000 端口)、Redis 已启动
"""
import json
import sys
import urllib.error
import urllib.request

import redis

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8000"


def post(path: str, body: dict, token: str = None):
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


if __name__ == "__main__":
    r = redis.Redis(host="127.0.0.1", port=6379, protocol=2, decode_responses=True)
    # ① 登录拿票
    _, body = post("/api/login", {"username": "admin", "password": "admin123"})
    token = body["token"]
    # ② 正常问一次(计数自动变 1)→ 期望 200
    print("① 正常问:", post("/api/chat/agent", {"question": "你好"}, token=token)[0])
    # ③ 手动把计数顶到 60(临界限)
    r.set("rate:admin", 60)
    print("② 已手动把 rate:admin 顶到 60")
    # ④ 再问一次(INCR 到 61 > 60)→ 期望 429
    status, body = post("/api/chat/agent", {"question": "你好"}, token=token)
    print("③ 顶满后再问:", status, body)
    # ⑤ 清场,恢复额度
    r.delete("rate:admin")
    print("④ 已清场,额度恢复")
